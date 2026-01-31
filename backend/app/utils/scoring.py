from typing import List, Dict
import numpy as np

def normalize_scores(recommendations: List[Dict], min_val: float = 0.6, max_val: float = 0.98) -> List[Dict]:
    """
    Normalize recommendation scores to a human-friendly range (e.g., 60% to 98%).
    This ensures variance in the UI while keeping scores 'encouraging'.
    """
    if not recommendations:
        return []
    
    scores = [r["score"] for r in recommendations]
    min_score = min(scores)
    max_score = max(scores)
    
    range_score = max_score - min_score
    
    for rec in recommendations:
        if range_score == 0:
            rec["score"] = max_val
        else:
            # Min-Max normalization to [0, 1]
            normalized = (rec["score"] - min_score) / range_score
            # Scale to target range [min_val, max_val]
            rec["score"] = min_val + (normalized * (max_val - min_val))
            
    return recommendations
