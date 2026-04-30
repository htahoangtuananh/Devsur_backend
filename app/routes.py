import hashlib
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Event, Insight, SavedInsight, Topic
from app.schemas import (
    DailyPackOut,
    EventCreate,
    EventOut,
    InsightOut,
    RandomRequest,
    SavedInsightCreate,
    SavedInsightOut,
    TopicOut,
)

router = APIRouter()


# ── Health ─────────────────────────────────────────────────────────────────

@router.get("/health")
async def health():
    return {"status": "ok"}


# ── Topics ─────────────────────────────────────────────────────────────────

@router.get("/topics", response_model=list[TopicOut])
def get_topics(db: Session = Depends(get_db)):
    """Return all topics."""
    return db.query(Topic).order_by(Topic.id).all()


# ── Daily Pack ─────────────────────────────────────────────────────────────

@router.get("/daily-pack", response_model=DailyPackOut)
def get_daily_pack(
    date: date = Query(default=None, description="Date in YYYY-MM-DD format"),
    topics: str = Query(default=None, description="Comma-separated topic slugs"),
    db: Session = Depends(get_db),
):
    """Deterministic daily pack — same date + topics = same pack."""
    pack_date = date or datetime.now().date()

    query = db.query(Insight)

    # Filter by topics if provided
    if topics:
        topic_slugs = [t.strip() for t in topics.split(",") if t.strip()]
        if topic_slugs:
            query = query.filter(Insight.topic.in_(topic_slugs))

    all_insights = query.order_by(Insight.id).all()

    if not all_insights:
        raise HTTPException(status_code=404, detail="No insights found for the given filters")

    # Deterministic selection seeded by date
    date_seed = int(hashlib.md5(f"{pack_date}:{settings.DAILY_PACK_SEED}".encode()).hexdigest(), 16)
    rng = __import__("random").Random(date_seed)

    pack = rng.sample(all_insights, min(settings.PACK_SIZE, len(all_insights)))

    return DailyPackOut(
        date=pack_date.isoformat(),
        insights=pack,
        total=len(pack),
    )


# ── Random ─────────────────────────────────────────────────────────────────

@router.get("/random", response_model=InsightOut)
def get_random(
    topics: str = Query(default=None, description="Comma-separated topic slugs"),
    exclude_ids: str = Query(default=None, description="Comma-separated insight IDs to exclude"),
    db: Session = Depends(get_db),
):
    """Return a single random insight, optionally filtered by topics and excluding seen IDs."""
    import random

    query = db.query(Insight)

    if topics:
        topic_slugs = [t.strip() for t in topics.split(",") if t.strip()]
        if topic_slugs:
            query = query.filter(Insight.topic.in_(topic_slugs))

    if exclude_ids:
        excluded = [eid.strip() for eid in exclude_ids.split(",") if eid.strip()]
        if excluded:
            query = query.filter(Insight.id.notin_(excluded))

    insights = query.all()

    if not insights:
        raise HTTPException(status_code=404, detail="No insights found for the given filters")

    return random.choice(insights)


# ── Insight by ID ──────────────────────────────────────────────────────────

@router.get("/insight/{insight_id}", response_model=InsightOut)
def get_insight_by_id(insight_id: str, db: Session = Depends(get_db)):
    """Get a single insight by its ID."""
    insight = db.query(Insight).filter(Insight.id == insight_id).first()
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    return insight


# ── Saved ──────────────────────────────────────────────────────────────────

@router.get("/saved", response_model=list[SavedInsightOut])
def get_saved(db: Session = Depends(get_db)):
    """List all saved insights for the default user."""
    return (
        db.query(SavedInsight)
        .filter(SavedInsight.user_id == settings.DEFAULT_USER_ID)
        .order_by(SavedInsight.saved_at.desc())
        .all()
    )


@router.post("/saved/{insight_id}", response_model=SavedInsightOut, status_code=201)
def save_insight(insight_id: str, db: Session = Depends(get_db)):
    """Save an insight."""
    insight = db.query(Insight).filter(Insight.id == insight_id).first()
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")

    existing = (
        db.query(SavedInsight)
        .filter(
            SavedInsight.insight_id == insight_id,
            SavedInsight.user_id == settings.DEFAULT_USER_ID,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Insight already saved")

    saved = SavedInsight(insight_id=insight_id, user_id=settings.DEFAULT_USER_ID)
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return saved


@router.delete("/saved/{insight_id}", status_code=204)
def delete_saved(insight_id: str, db: Session = Depends(get_db)):
    """Unsave an insight."""
    saved = (
        db.query(SavedInsight)
        .filter(
            SavedInsight.insight_id == insight_id,
            SavedInsight.user_id == settings.DEFAULT_USER_ID,
        )
        .first()
    )
    if not saved:
        raise HTTPException(status_code=404, detail="Saved insight not found")

    db.delete(saved)
    db.commit()


# ── Events ─────────────────────────────────────────────────────────────────

@router.post("/events", response_model=EventOut, status_code=201)
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    """Track a view/save/share/random event."""
    if event.insight_id:
        insight = db.query(Insight).filter(Insight.id == event.insight_id).first()
        if not insight:
            raise HTTPException(status_code=404, detail="Insight not found")

    db_event = Event(
        insight_id=event.insight_id,
        event_type=event.event_type,
        user_id=event.user_id,
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event