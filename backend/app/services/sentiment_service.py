from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class SentimentService:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def analyze_hype(self, comments: List[str]) -> Dict:
        """
        Analyze a list of comments and return a hype score and summary.
        """
        if not comments:
            return {
                "hype_score": 50,
                "sentiment_distribution": {"pos": 0, "neg": 0, "neu": 1.0},
                "summary": "No community buzz detected yet.",
                "comment_count": 0
            }

        pos_scores = []
        compound_scores = []

        for comment in comments:
            vs = self.analyzer.polarity_scores(comment)
            compound_scores.append(vs['compound'])
            pos_scores.append(vs['pos'])

        # Normalize compound score (-1 to 1) to a 0-100 scale
        avg_compound = sum(compound_scores) / len(compound_scores)
        hype_score = int(((avg_compound + 1) / 2) * 100)

        # Determine summary label
        if avg_compound >= 0.5:
            summary = "Overwhelmingly Positive"
        elif avg_compound >= 0.1:
            summary = "Mostly Positive"
        elif avg_compound <= -0.5:
            summary = "Strongly Mixed/Critical"
        elif avg_compound <= -0.1:
            summary = "Mixed"
        else:
            summary = "Neutral/Cautious"

        return {
            "hype_score": hype_score,
            "avg_sentiment": avg_compound,
            "summary": summary,
            "comment_count": len(comments)
        }
