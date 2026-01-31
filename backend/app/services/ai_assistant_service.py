import os
import google.generativeai as genai
from sqlalchemy.orm import Session
from app.models import Movie, User
from app.services.ml_recommendations import ml_engine
from app.services.advanced_recommendations import MoodBasedRecommendation
import json
import re
import random

class AIAssistantService:
    _model = None

    @staticmethod
    def _get_model():
        if AIAssistantService._model is None:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                return None
            genai.configure(api_key=api_key)
            
            try:
                # Dynamically find the best available model
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                if not available_models:
                    return None
                
                # Prioritize flash, then pro, then whatever is first
                selected_model = next((m for m in available_models if 'flash' in m), 
                                     next((m for m in available_models if 'pro' in m), available_models[0]))
                
                print(f"DEBUG: CineBot selecting model: {selected_model}")
                AIAssistantService._model = genai.GenerativeModel(selected_model)
            except Exception as e:
                print(f"DEBUG: Error listing models: {e}")
                # Fallback to a common default if listing fails
                AIAssistantService._model = genai.GenerativeModel('gemini-1.5-flash')
                
        return AIAssistantService._model

    @staticmethod
    def process_query(user_id: int, query: str, db: Session):
        model = AIAssistantService._get_model()
        if not model:
            return {
                "content": "A system error occurred: Neural Link (Gemini API) not configured. Please check .env file.",
                "movies": []
            }

        system_prompt = """
        You are CineBot AI, a sophisticated, empathetic, and professional cinematic assistant for the 'CineAI' platform.
        Your goal is to understand the user's emotional state, life context, and movie preferences.

        COMMUNICATION STYLE:
        - Empathetic and warm.
        - Cinematic and high-tech (use phrases like 'neural scan', 'system analysis', 'archival retrieval').
        - Concise but meaningful.

        INTENT DETECTION:
        You must analyze the user query and provide a response in JSON format (strictly JSON, no extra text).
        Identify one of the following intentions:
        1. 'recommend': General recommendation based on history.
        2. 'mood': Recommendations based on emotional state/vibe (e.g. happy, sad, lonely, excited, chill, thoughtful).
        3. 'genre': Searching for a specific category (e.g. action, scifi, horror).
        4. 'director': Searching for movies by a specific director name.
        5. 'search': Finding a specific movie by name.
        6. 'informational': General chat or greetings.

        RESPONSE STRUCTURE:
        Return a JSON object with:
        {
            "empathy_response": "Your spoken response to the user, reflecting their context and emotion.",
            "intent": "recommend|mood|genre|director|search|informational",
            "search_term": "A keyword for search (genre name, movie title, director name, or mood name)",
            "context_note": "A internal note about the detection (e.g. 'user is asking for Nolan')"
        }

        Example for 'I'm feeling lonely':
        {
            "empathy_response": "I'm sorry to hear that. System logic suggests that a soul-nourishing cinematic journey can bridge the gap. I've retrieved some comforting masterpieces for you.",
            "intent": "mood",
            "search_term": "sad",
            "context_note": "lonely context"
        }
        """

        try:
            response = model.generate_content(f"{system_prompt}\n\nUser Query: {query}")
            json_text = response.text
            print(f"DEBUG: Raw AI Response: {json_text}")
            
            if "```json" in json_text:
                json_text = json_text.split("```json")[1].split("```")[0].strip()
            elif "```" in json_text:
                json_text = json_text.split("```")[1].split("```")[0].strip()
            
            print(f"DEBUG: Extracted JSON: {json_text}")
            ai_data = json.loads(json_text)
            
            # Now map AI intent to our local DB/Engine
            intent = ai_data.get("intent")
            search_term = ai_data.get("search_term", "").lower()
            empathy_text = ai_data.get("empathy_response")

            if intent == "mood":
                return AIAssistantService._get_mood_recommendations(user_id, search_term, db, empathy_text)
            elif intent == "genre":
                return AIAssistantService._get_genre_recommendations(search_term, db, empathy_text)
            elif intent == "director":
                return AIAssistantService._get_director_recommendations(search_term, db, empathy_text)
            elif intent == "search":
                return AIAssistantService._search_movie(search_term, db, empathy_text)
            elif intent == "recommend":
                return AIAssistantService._get_general_recommendations(user_id, db, empathy_text)
            else:
                return {
                    "content": empathy_text,
                    "movies": []
                }

        except Exception as e:
            print(f"Gemini Error: {e}")
            return {
                "content": "My central neural processors are experiencing turbulence. I'm reverting to local backup systems. How can I help?",
                "movies": []
            }

    @staticmethod
    def _get_general_recommendations(user_id: int, db: Session, content: str):
        if not ml_engine.is_trained:
            ml_engine.train_model(db)
        
        recs = ml_engine.get_ml_recommendations(user_id, db, limit=20) # Get larger pool
        movies = []
        for r in recs:
            movie = db.query(Movie).filter(Movie.id == r["movie_id"]).first()
            if movie:
                movies.append(movie)
        
        # Add variety by sampling
        sampled_movies = random.sample(movies, min(len(movies), 4))
        
        return {
            "content": content,
            "movies": sampled_movies
        }

    @staticmethod
    def _get_mood_recommendations(user_id: int, mood: str, db: Session, content: str):
        # Map AI mood to our supported internal moods
        supported_moods = ["happy", "sad", "scared", "relaxed", "thoughtful", "excited"]
        target_mood = "happy"
        for sm in supported_moods:
            if sm in mood:
                target_mood = sm
                break
                
        recs = MoodBasedRecommendation.get_mood_recommendations(user_id, target_mood, db, limit=20) # Larger pool
        movies = []
        for r in recs:
            movie = db.query(Movie).filter(Movie.id == r["movie_id"]).first()
            if movie:
                movies.append(movie)
        
        # Shuffle for variety
        random.shuffle(movies)
        
        return {
            "content": content,
            "movies": movies[:4]
        }

    @staticmethod
    def _get_genre_recommendations(genre: str, db: Session, content: str):
        movies = db.query(Movie).filter(Movie.genre.ilike(f"%{genre}%")).order_by(Movie.popularity.desc()).limit(20).all()
        random.shuffle(movies)
        return {
            "content": content,
            "movies": movies[:4]
        }

    @staticmethod
    def _get_director_recommendations(director: str, db: Session, content: str):
        movies = db.query(Movie).filter(Movie.director.ilike(f"%{director}%")).order_by(Movie.popularity.desc()).limit(10).all()
        
        if not movies:
            return {
                "content": f"I couldn't find any movies directed by '{director}' in our primary archive. I'll continue indexing for future queries.",
                "movies": []
            }
            
        return {
            "content": content,
            "movies": movies
        }

    @staticmethod
    def _search_movie(title: str, db: Session, content: str):
        movie = db.query(Movie).filter(Movie.title.ilike(f"%{title}%")).first()
        if movie:
            return {
                "content": content,
                "movies": [movie]
            }
        else:
            return {
                "content": f"I analyzed my archives but couldn't find a direct match for '{title}'. Here are some trending picks instead.",
                "movies": db.query(Movie).order_by(Movie.popularity.desc()).limit(3).all()
            }
