from datetime import datetime
from pydantic import BaseModel, Field


# ── Topic ──────────────────────────────────────────────────────────────────

class TopicBase(BaseModel):
    domain: str
    name: str
    slug: str
    description: str = ""


class TopicOut(TopicBase):
    id: int

    model_config = {"from_attributes": True}


# ── Insight ────────────────────────────────────────────────────────────────

INSIGHT_TYPES = [
    "counterintuitive_truth",
    "surprising_fact",
    "misconception",
    "expert_heuristic",
    "underrated_concept",
]

DOMAINS = ["ai", "data", "software"]


class InsightBase(BaseModel):
    domain: str = Field(..., description="ai | data | software")
    topic: str
    type: str = Field(..., description=f"One of: {', '.join(INSIGHT_TYPES)}")
    hook: str
    insight: str
    why_it_matters: str


class InsightCreate(InsightBase):
    pass


class InsightOut(InsightBase):
    id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class InsightDetail(InsightOut):
    """Full insight with why_it_matters expanded."""
    pass


class InsightCard(BaseModel):
    """Lightweight card for widget/home screen."""
    id: str
    hook: str
    insight: str
    type: str
    topic: str

    model_config = {"from_attributes": True}


# ── Daily Pack ─────────────────────────────────────────────────────────────

class DailyPackOut(BaseModel):
    date: str
    insights: list[InsightOut]
    total: int


# ── Saved ──────────────────────────────────────────────────────────────────

class SavedInsightCreate(BaseModel):
    insight_id: str


class SavedInsightOut(BaseModel):
    id: int
    insight_id: str
    user_id: str
    saved_at: datetime
    insight: InsightOut | None = None

    model_config = {"from_attributes": True}


# ── Event ──────────────────────────────────────────────────────────────────

class EventCreate(BaseModel):
    insight_id: str | None = None
    event_type: str = Field(..., description="view | save | share | random")
    user_id: str = "default"


class EventOut(BaseModel):
    id: int
    insight_id: str | None
    event_type: str
    user_id: str
    timestamp: datetime

    model_config = {"from_attributes": True}


# ── Random ──────────────────────────────────────────────────────────────────

class RandomRequest(BaseModel):
    topics: list[str] | None = None
    exclude_ids: list[str] | None = None
    user_id: str = "default"