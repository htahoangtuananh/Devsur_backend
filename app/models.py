import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey, Integer, func
from sqlalchemy.dialects.sqlite import BLOB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    domain: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")

    def __repr__(self):
        return f"<Topic {self.slug}>"


class Insight(Base):
    __tablename__ = "insights"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    domain: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    topic: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # counterintuitive_truth, surprising_fact, misconception, expert_heuristic, underrated_concept
    hook: Mapped[str] = mapped_column(Text, nullable=False)
    insight: Mapped[str] = mapped_column(Text, nullable=False)
    why_it_matters: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    def __repr__(self):
        return f"<Insight {self.id[:8]} ({self.topic})>"


class SavedInsight(Base):
    __tablename__ = "saved_insights"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    insight_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("insights.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(String(100), default="default", index=True, nullable=False)
    saved_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    insight: Mapped["Insight"] = relationship("Insight", lazy="joined")

    def __repr__(self):
        return f"<SavedInsight user={self.user_id} insight={self.insight_id[:8]}>"


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    insight_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("insights.id", ondelete="SET NULL"), nullable=True, index=True
    )
    event_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # view, save, share, random
    user_id: Mapped[str] = mapped_column(String(100), default="default", index=True, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    def __repr__(self):
        return f"<Event {self.event_type} user={self.user_id}>"