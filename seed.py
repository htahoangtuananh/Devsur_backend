#!/usr/bin/env python3
"""Seed the database with insights and topics."""

import json
import sys
from pathlib import Path

from sqlalchemy.orm import Session

from app.database import engine, SessionLocal
from app.models import Base, Topic, Insight

DATA_DIR = Path(__file__).parent / "data"


def seed_topics(db: Session):
    """Seed topics from topics.json."""
    topics_file = DATA_DIR / "topics.json"
    if not topics_file.exists():
        print("❌ topics.json not found")
        return 0

    with open(topics_file) as f:
        topics = json.load(f)

    count = 0
    for t in topics:
        existing = db.query(Topic).filter(Topic.slug == t["slug"]).first()
        if not existing:
            db.add(Topic(**t))
            count += 1

    db.commit()
    print(f"✅ Seeded {count} topics ({len(topics)} total)")
    return count


def seed_insights(db: Session):
    """Seed insights from insights.json."""
    insights_file = DATA_DIR / "insights.json"
    if not insights_file.exists():
        print("❌ insights.json not found")
        return 0

    with open(insights_file) as f:
        insights = json.load(f)

    count = 0
    for i in insights:
        existing = db.query(Insight).filter(Insight.insight == i["insight"]).first()
        if not existing:
            db.add(Insight(**i))
            count += 1

    db.commit()
    print(f"✅ Seeded {count} insights ({len(insights)} total)")
    return count


def main():
    # Create tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        seed_topics(db)
        seed_insights(db)
    finally:
        db.close()

    print("🎉 Seeding complete!")


if __name__ == "__main__":
    main()