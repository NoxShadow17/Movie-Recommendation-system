from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models import User, FriendRequest, Friendship, FriendRequestStatus
from app.schemas import FriendRequestResponse, FriendResponse
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/friends", tags=["friends"])


@router.get("/requests/sent", response_model=List[FriendRequestResponse])
def get_sent_friend_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all friend requests sent by the current user"""
    requests = db.query(FriendRequest).filter(
        FriendRequest.sender_id == current_user.id
    ).all()
    
    result = []
    for req in requests:
        receiver = db.query(User).filter(User.id == req.receiver_id).first()
        result.append({
            "id": req.id,
            "sender_id": req.sender_id,
            "receiver_id": req.receiver_id,
            "status": req.status,
            "created_at": req.created_at,
            "receiver_username": receiver.username if receiver else None,
            "receiver_email": receiver.email if receiver else None
        })
    
    return result


@router.get("/requests/received", response_model=List[FriendRequestResponse])
def get_received_friend_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all friend requests received by the current user"""
    requests = db.query(FriendRequest).filter(
        FriendRequest.receiver_id == current_user.id,
        FriendRequest.status == FriendRequestStatus.PENDING
    ).all()
    
    result = []
    for req in requests:
        sender = db.query(User).filter(User.id == req.sender_id).first()
        result.append({
            "id": req.id,
            "sender_id": req.sender_id,
            "receiver_id": req.receiver_id,
            "status": req.status,
            "created_at": req.created_at,
            "sender_username": sender.username if sender else None,
            "sender_email": sender.email if sender else None
        })
    
    return result


@router.post("/requests/send/{user_id}")
def send_friend_request(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a friend request to another user"""
    # Check if user exists
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if already friends (active friendship only)
    existing_friendship = db.query(Friendship).filter(
        ((Friendship.user1_id == current_user.id) & (Friendship.user2_id == user_id)) |
        ((Friendship.user1_id == user_id) & (Friendship.user2_id == current_user.id)),
        Friendship.is_active == True
    ).first()
    
    if existing_friendship:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already friends with this user"
        )
    
    # Check if there's already a pending request
    existing_request = db.query(FriendRequest).filter(
        FriendRequest.sender_id == current_user.id,
        FriendRequest.receiver_id == user_id,
        FriendRequest.status == FriendRequestStatus.PENDING
    ).first()
    
    if existing_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Friend request already sent"
        )
    
    # Check if target user has sent request to current user
    reverse_request = db.query(FriendRequest).filter(
        FriendRequest.sender_id == user_id,
        FriendRequest.receiver_id == current_user.id,
        FriendRequest.status == FriendRequestStatus.PENDING
    ).first()
    
    if reverse_request:
        # Auto-accept if there's a mutual pending request
        reverse_request.status = FriendRequestStatus.ACCEPTED
        
        # Create friendship
        friendship = Friendship(
            user1_id=current_user.id,
            user2_id=user_id
        )
        db.add(friendship)
        db.commit()
        
        return {"message": "Friend request accepted! You are now friends."}
    
    # Create new friend request
    friend_request = FriendRequest(
        sender_id=current_user.id,
        receiver_id=user_id,
        status=FriendRequestStatus.PENDING
    )
    
    db.add(friend_request)
    db.commit()
    
    return {"message": "Friend request sent successfully"}


@router.post("/requests/accept/{request_id}")
def accept_friend_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Accept a friend request"""
    friend_request = db.query(FriendRequest).filter(
        FriendRequest.id == request_id,
        FriendRequest.receiver_id == current_user.id,
        FriendRequest.status == FriendRequestStatus.PENDING
    ).first()
    
    if not friend_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friend request not found or already processed"
        )
    
    # Update request status
    friend_request.status = FriendRequestStatus.ACCEPTED
    
    # Create friendship
    friendship = Friendship(
        user1_id=friend_request.sender_id,
        user2_id=friend_request.receiver_id
    )
    
    db.add(friendship)
    db.commit()
    
    return {"message": "Friend request accepted successfully"}


@router.post("/requests/reject/{request_id}")
def reject_friend_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reject a friend request"""
    friend_request = db.query(FriendRequest).filter(
        FriendRequest.id == request_id,
        FriendRequest.receiver_id == current_user.id,
        FriendRequest.status == FriendRequestStatus.PENDING
    ).first()
    
    if not friend_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friend request not found or already processed"
        )
    
    # Update request status
    friend_request.status = FriendRequestStatus.REJECTED
    db.commit()
    
    return {"message": "Friend request rejected successfully"}


@router.post("/requests/cancel/{request_id}")
def cancel_friend_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a friend request sent by the current user"""
    friend_request = db.query(FriendRequest).filter(
        FriendRequest.id == request_id,
        FriendRequest.sender_id == current_user.id,
        FriendRequest.status == FriendRequestStatus.PENDING
    ).first()
    
    if not friend_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friend request not found or already processed"
        )
    
    # Update request status
    friend_request.status = FriendRequestStatus.CANCELLED
    db.commit()
    
    return {"message": "Friend request cancelled successfully"}


@router.get("/list", response_model=List[FriendResponse])
def get_friends(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of current user's friends with pagination"""
    friendships = db.query(Friendship).filter(
        ((Friendship.user1_id == current_user.id) | (Friendship.user2_id == current_user.id)),
        Friendship.is_active == True
    ).offset(skip).limit(limit).all()
    
    result = []
    for friendship in friendships:
        # Determine which user is the friend
        friend_id = friendship.user2_id if friendship.user1_id == current_user.id else friendship.user1_id
        friend = db.query(User).filter(User.id == friend_id).first()
        
        if friend:
            result.append({
                "id": friend.id,
                "username": friend.username,
                "email": friend.email,
                "full_name": friend.full_name,
                "profile_picture": friend.profile_picture,
                "created_at": friendship.created_at
            })
    
    return result


@router.delete("/remove/{friend_id}")
def remove_friend(
    friend_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a friend"""
    friendship = db.query(Friendship).filter(
        ((Friendship.user1_id == current_user.id) & (Friendship.user2_id == friend_id)) |
        ((Friendship.user1_id == friend_id) & (Friendship.user2_id == current_user.id)),
        Friendship.is_active == True
    ).first()
    
    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friendship not found"
        )
    
    # Deactivate friendship instead of deleting
    friendship.is_active = False
    db.commit()
    
    return {"message": "Friend removed successfully"}


@router.get("/search")
def search_users(
    query: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search for users to add as friends"""
    if not query or len(query) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query must be at least 3 characters long"
        )
    
    # Search users by username or email (excluding current user)
    users = db.query(User).filter(
        User.id != current_user.id,
        User.is_active == True,
        (
            (User.username.ilike(f"%{query}%")) |
            (User.email.ilike(f"%{query}%")) |
            (User.full_name.ilike(f"%{query}%"))
        )
    ).limit(20).all()
    
    result = []
    for user in users:
        # Check friendship status
        friendship = db.query(Friendship).filter(
            ((Friendship.user1_id == current_user.id) & (Friendship.user2_id == user.id)) |
            ((Friendship.user1_id == user.id) & (Friendship.user2_id == current_user.id)),
            Friendship.is_active == True
        ).first()
        
        # Check pending requests
        sent_request = db.query(FriendRequest).filter(
            FriendRequest.sender_id == current_user.id,
            FriendRequest.receiver_id == user.id,
            FriendRequest.status == FriendRequestStatus.PENDING
        ).first()
        
        received_request = db.query(FriendRequest).filter(
            FriendRequest.sender_id == user.id,
            FriendRequest.receiver_id == current_user.id,
            FriendRequest.status == FriendRequestStatus.PENDING
        ).first()
        
        status_info = "available"
        if friendship:
            status_info = "friends"
        elif sent_request:
            status_info = "request_sent"
        elif received_request:
            status_info = "request_received"
        
        result.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "profile_picture": user.profile_picture,
            "status": status_info
        })
    
    return result


@router.get("/stats")
def get_friend_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get friend statistics for the current user"""
    # Count friends
    friend_count = db.query(Friendship).filter(
        ((Friendship.user1_id == current_user.id) | (Friendship.user2_id == current_user.id)),
        Friendship.is_active == True
    ).count()
    
    # Count pending sent requests
    sent_requests = db.query(FriendRequest).filter(
        FriendRequest.sender_id == current_user.id,
        FriendRequest.status == FriendRequestStatus.PENDING
    ).count()
    
    # Count pending received requests
    received_requests = db.query(FriendRequest).filter(
        FriendRequest.receiver_id == current_user.id,
        FriendRequest.status == FriendRequestStatus.PENDING
    ).count()
    
    return {
        "total_friends": friend_count,
        "pending_sent_requests": sent_requests,
        "pending_received_requests": received_requests,
        "total_pending_requests": sent_requests + received_requests
    }
