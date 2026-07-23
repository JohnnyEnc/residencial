from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import AdminUser, CurrentUser, DbSession
from app.models.announcement import Announcement, AnnouncementRead
from app.models.user import UserRole
from app.schemas.announcement import AnnouncementCreate, AnnouncementOut

router = APIRouter(prefix="/announcements", tags=["announcements"])


def serialize(ann: Announcement, read: bool) -> AnnouncementOut:
    return AnnouncementOut(
        id=ann.id,
        title=ann.title,
        body=ann.body,
        priority=ann.priority,
        published_at=ann.published_at,
        expires_at=ann.expires_at,
        created_by=ann.created_by,
        read=read,
    )


@router.get("", response_model=list[AnnouncementOut])
def list_announcements(db: DbSession, user: CurrentUser):
    now = datetime.now(timezone.utc)
    anns = (
        db.query(Announcement)
        .filter((Announcement.expires_at.is_(None)) | (Announcement.expires_at > now))
        .order_by(Announcement.published_at.desc())
        .all()
    )
    reads = {
        r.announcement_id
        for r in db.query(AnnouncementRead).filter(AnnouncementRead.user_id == user.id).all()
    }
    return [serialize(a, a.id in reads) for a in anns]


@router.post("", response_model=AnnouncementOut, status_code=status.HTTP_201_CREATED)
def create_announcement(payload: AnnouncementCreate, db: DbSession, admin: AdminUser):
    ann = Announcement(
        title=payload.title,
        body=payload.body,
        priority=payload.priority,
        expires_at=payload.expires_at,
        created_by=admin.id,
    )
    db.add(ann)
    db.commit()
    db.refresh(ann)
    return serialize(ann, False)


@router.post("/{announcement_id}/read", response_model=AnnouncementOut)
def mark_read(announcement_id: int, db: DbSession, user: CurrentUser):
    ann = db.get(Announcement, announcement_id)
    if not ann:
        raise HTTPException(status_code=404, detail="Aviso no encontrado")
    existing = (
        db.query(AnnouncementRead)
        .filter(
            AnnouncementRead.announcement_id == announcement_id,
            AnnouncementRead.user_id == user.id,
        )
        .first()
    )
    if not existing:
        db.add(AnnouncementRead(announcement_id=announcement_id, user_id=user.id))
        db.commit()
    return serialize(ann, True)


@router.delete("/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_announcement(announcement_id: int, db: DbSession, _: AdminUser):
    ann = db.get(Announcement, announcement_id)
    if not ann:
        raise HTTPException(status_code=404, detail="Aviso no encontrado")
    db.delete(ann)
    db.commit()
