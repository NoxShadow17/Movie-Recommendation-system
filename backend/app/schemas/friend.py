from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class FriendRequestBase(BaseModel):
    sender_id: int
    receiver_id: int
    status: str


class FriendRequestCreate(BaseModel):
    receiver_id: int


class FriendRequestResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    status: str
    created_at: datetime
    sender_username: Optional[str] = None
    sender_email: Optional[str] = None
    receiver_username: Optional[str] = None
    receiver_email: Optional[str] = None

    class Config:
        from_attributes = True


class FriendResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    profile_picture: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FriendSearchResult(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    profile_picture: Optional[str] = None
    status: str  # available, friends, request_sent, request_received

    class Config:
        from_attributes = True


class FriendStats(BaseModel):
    total_friends: int
    pending_sent_requests: int
    pending_received_requests: int
    total_pending_requests: int


class FriendActivity(BaseModel):
    friend_id: int
    friend_username: str
    movie_id: int
    movie_title: str
    rating: Optional[float] = None
    review: Optional[str] = None
    mood: Optional[str] = None
    activity_type: str  # rated, reviewed, watched
    created_at: datetime

    class Config:
        from_attributes = True


class SocialRecommendation(BaseModel):
    movie_id: int
    movie_title: str
    movie_poster: Optional[str] = None
    friend_count: int
    avg_friend_rating: Optional[float] = None
    reason: str
    score: float

    class Config:
        from_attributes = True
