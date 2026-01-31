import os
from googleapiclient.discovery import build
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class YouTubeService:
    def __init__(self):
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            logger.warning("YOUTUBE_API_KEY not found. YouTube features will be limited.")
            self.youtube = None
        else:
            self.youtube = build("youtube", "v3", developerKey=self.api_key)

    def get_trailer_comments(self, movie_title: str, max_comments: int = 50) -> List[str]:
        """
        Search for the official trailer of a movie and fetch user comments.
        """
        if not self.youtube:
            return []

        try:
            # 1. Search for the trailer
            search_response = self.youtube.search().list(
                q=f"{movie_title} official trailer",
                part="id,snippet",
                maxResults=1,
                type="video"
            ).execute()

            print(f"DEBUG: Search response for '{movie_title}': {search_response}")

            if not search_response.get("items"):
                print(f"DEBUG: No items found for '{movie_title}'")
                return []

            video_id = search_response["items"][0]["id"]["videoId"]

            # 2. Get comment threads
            comments_response = self.youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                textFormat="plainText",
                maxResults=max_comments
            ).execute()

            comments = []
            for item in comments_response.get("items", []):
                comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                comments.append(comment)

            return comments

        except Exception as e:
            # Check for Quota Exceeded (403 or 429)
            if "quotaExceeded" in str(e) or "403" in str(e) or "429" in str(e):
                logger.warning(f"YouTube API Quota Exceeded for {movie_title}. Switching to simulation mode.")
                return None # Signal to caller to use fallback/mock data
            
            logger.error(f"Error fetching YouTube comments for {movie_title}: {e}")
            return []
