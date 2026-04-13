# app/api/v1/social.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timezone

from app.database import get_db
from app.models.user import User
from app.models.social import UserProfile, Follow
from app.models.activity import Activity
from app.api.deps import get_current_user
from pydantic import BaseModel, ConfigDict


router = APIRouter(prefix="/social", tags=["social"])


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_entity_id: int
    username: str
    avatar_url: Optional[str]
    bio: Optional[str]
    website: Optional[str]
    social_links: Optional[dict]
    reputation: float
    followers_count: int
    following_count: int
    problems_count: int


class UserProfileUpdate(BaseModel):
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    website: Optional[str] = None
    social_links: Optional[dict] = None


@router.get("/profile/{user_id}", response_model=UserProfileResponse)
def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db),
):
    """Получить профиль пользователя"""
    user = db.query(User).filter_by(entity_id=user_id, is_current=True).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = (
        db.query(UserProfile)
        .filter_by(user_entity_id=user_id, is_current=True)
        .first()
    )

    followers_count = (
        db.query(Follow)
        .filter_by(following_entity_id=user_id, is_current=True)
        .count()
    )

    following_count = (
        db.query(Follow)
        .filter_by(follower_entity_id=user_id, is_current=True)
        .count()
    )

    from app.models.problem import Problem
    problems_count = (
        db.query(Problem)
        .filter_by(author_entity_id=user_id, version=1)
        .count()
    )

    return UserProfileResponse(
        user_entity_id=user.entity_id,
        username=user.username,
        avatar_url=profile.avatar_url if profile else None,
        bio=profile.bio if profile else None,
        website=profile.website if profile else None,
        social_links=profile.social_links if profile else None,
        reputation=user.reputation,
        followers_count=followers_count,
        following_count=following_count,
        problems_count=problems_count,
    )


@router.patch("/profile", response_model=UserProfileResponse)
def update_my_profile(
    data: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Обновить свой профиль"""
    from app.services.versioning import create_new_version

    # Найти текущий профиль пользователя по user_entity_id
    profile = db.query(UserProfile).filter_by(
        user_entity_id=current_user.entity_id,
        is_current=True
    ).first()

    if not profile:
        # Создать профиль если его нет
        entity_id = UserProfile.next_entity_id(db)
        profile = UserProfile(
            entity_id=entity_id,
            version=1,
            is_current=True,
            user_entity_id=current_user.entity_id,
            changed_by_id=current_user.entity_id,
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    # Обновить поля через create_new_version
    update_data = data.model_dump(exclude_unset=True)
    if update_data:
        create_new_version(
            db=db,
            model_class=UserProfile,
            entity_id=profile.entity_id,
            changed_by_id=current_user.entity_id,
            change_reason="profile_updated",
            **update_data
        )

    return get_user_profile(current_user.entity_id, db)


@router.post("/follow/{user_id}")
def follow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Подписаться на пользователя"""
    if user_id == current_user.entity_id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")

    target_user = db.query(User).filter_by(entity_id=user_id, is_current=True).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    existing = (
        db.query(Follow)
        .filter_by(
            follower_entity_id=current_user.entity_id,
            following_entity_id=user_id,
            is_current=True,
        )
        .first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="Already following")

    entity_id = Follow.next_entity_id(db)
    follow = Follow(
        entity_id=entity_id,
        version=1,
        is_current=True,
        follower_entity_id=current_user.entity_id,
        following_entity_id=user_id,
        changed_by_id=current_user.entity_id,
    )
    db.add(follow)
    db.commit()

    return {"message": "Successfully followed"}


@router.delete("/follow/{user_id}")
def unfollow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Отписаться от пользователя"""
    follow = (
        db.query(Follow)
        .filter_by(
            follower_entity_id=current_user.entity_id,
            following_entity_id=user_id,
            is_current=True,
        )
        .first()
    )

    if not follow:
        raise HTTPException(status_code=404, detail="Not following")

    follow.is_current = False
    from datetime import datetime
    follow.superseded_at = datetime.now(timezone.utc)
    db.commit()

    return {"message": "Successfully unfollowed"}


@router.get("/follow/{user_id}/status")
def get_follow_status(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Проверить статус подписки на пользователя"""
    follow = (
        db.query(Follow)
        .filter_by(
            follower_entity_id=current_user.entity_id,
            following_entity_id=user_id,
            is_current=True,
        )
        .first()
    )

    return {"is_following": follow is not None}


@router.get("/feed")
def get_activity_feed(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Получить ленту активности подписок"""
    # Получить ID пользователей, на которых подписан
    following_ids = [
        f.following_entity_id
        for f in db.query(Follow)
        .filter_by(follower_entity_id=current_user.entity_id, is_current=True)
        .all()
    ]

    if not following_ids:
        return {"activities": [], "total": 0}

    # Получить активность
    activities = (
        db.query(Activity)
        .filter(
            Activity.user_entity_id.in_(following_ids),
            Activity.is_current,
        )
        .order_by(Activity.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    total = (
        db.query(Activity)
        .filter(
            Activity.user_entity_id.in_(following_ids),
            Activity.is_current,
        )
        .count()
    )

    return {
        "activities": [
            {
                "id": a.entity_id,
                "user_id": a.user_entity_id,
                "action_type": a.action_type,
                "target_type": a.target_type,
                "target_id": a.target_entity_id,
                "description": a.description,
                "created_at": a.created_at.isoformat(),
            }
            for a in activities
        ],
        "total": total,
    }
