"""Generate personalized listening insights using Claude API."""

import json
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.db.models import (
    AudioFeature,
    DailyListeningSummary,
    Insight,
    ListeningHistory,
    Track,
)


def _build_context(session: Session) -> dict:
    """Gather stats to feed to the LLM."""
    total_plays = session.query(func.count(ListeningHistory.id)).scalar() or 0
    unique_tracks = (
        session.query(func.count(func.distinct(ListeningHistory.track_id))).scalar() or 0
    )
    unique_artists = (
        session.query(func.count(func.distinct(Track.artist_name)))
        .join(ListeningHistory, ListeningHistory.track_id == Track.id)
        .scalar() or 0
    )

    # Top 5 artists by play count
    top_artists = (
        session.query(Track.artist_name, func.count().label("cnt"))
        .join(ListeningHistory, ListeningHistory.track_id == Track.id)
        .group_by(Track.artist_name)
        .order_by(func.count().desc())
        .limit(5)
        .all()
    )

    # Top 5 tracks
    top_tracks = (
        session.query(Track.name, Track.artist_name, func.count().label("cnt"))
        .join(ListeningHistory, ListeningHistory.track_id == Track.id)
        .group_by(Track.id)
        .order_by(func.count().desc())
        .limit(5)
        .all()
    )

    # Average audio features
    avg_features = session.query(
        func.avg(AudioFeature.energy),
        func.avg(AudioFeature.valence),
        func.avg(AudioFeature.danceability),
        func.avg(AudioFeature.acousticness),
    ).first()

    # Recent daily summaries
    recent_days = (
        session.query(DailyListeningSummary)
        .order_by(DailyListeningSummary.date.desc())
        .limit(7)
        .all()
    )

    return {
        "total_plays": total_plays,
        "unique_tracks": unique_tracks,
        "unique_artists": unique_artists,
        "top_artists": [{"name": a[0], "plays": a[1]} for a in top_artists],
        "top_tracks": [{"name": t[0], "artist": t[1], "plays": t[2]} for t in top_tracks],
        "avg_energy": round(avg_features[0], 3) if avg_features[0] else None,
        "avg_valence": round(avg_features[1], 3) if avg_features[1] else None,
        "avg_danceability": round(avg_features[2], 3) if avg_features[2] else None,
        "avg_acousticness": round(avg_features[3], 3) if avg_features[3] else None,
        "recent_daily_plays": [
            {"date": d.date, "plays": d.total_plays} for d in recent_days
        ],
    }


def generate_insights(session: Session) -> list[str]:
    """Generate insights using Claude API. Falls back to rule-based if no API key."""
    context = _build_context(session)

    from src.config import settings
    api_key = settings.anthropic_api_key
    if api_key:
        return _generate_with_llm(session, context, api_key)
    else:
        return _generate_rule_based(session, context)


def _generate_with_llm(session: Session, context: dict, api_key: str) -> list[str]:
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""You are a music analytics assistant analyzing a user's Spotify listening data.

Here is their data:
- Total plays: {context['total_plays']}
- Unique tracks: {context['unique_tracks']}, Unique artists: {context['unique_artists']}
- Top artists: {json.dumps(context['top_artists'])}
- Top tracks: {json.dumps(context['top_tracks'])}
- Average audio features: energy={context['avg_energy']}, valence={context['avg_valence']}, danceability={context['avg_danceability']}, acousticness={context['avg_acousticness']}
- Recent daily play counts: {json.dumps(context['recent_daily_plays'])}

Generate exactly 3 short, specific, personalized insights about their listening habits.
Each insight should be 1-2 sentences, conversational, and interesting.
Focus on patterns, moods, and behavior — not just restating numbers.
Return them as a JSON array of 3 strings. No markdown, just the JSON array."""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )

    try:
        insights = json.loads(message.content[0].text)
    except (json.JSONDecodeError, IndexError):
        insights = [message.content[0].text]

    # Store in DB
    for text in insights:
        session.add(Insight(
            insight_type="weekly",
            content=text,
            metadata_json=json.dumps(context),
            generated_at=datetime.utcnow(),
        ))
    session.commit()
    print(f"  Generated {len(insights)} LLM insights.")
    return insights


def _generate_rule_based(session: Session, context: dict) -> list[str]:
    """Fallback insights without an LLM."""
    insights = []

    if context["top_artists"]:
        top = context["top_artists"][0]
        insights.append(
            f"Your most-played artist is {top['name']} with {top['plays']} plays — "
            f"that's {round(top['plays'] / max(context['total_plays'], 1) * 100)}% of your listening."
        )

    if context["avg_valence"] is not None:
        mood = "upbeat and positive" if context["avg_valence"] > 0.5 else "mellow and reflective"
        insights.append(
            f"Your music leans {mood} with an average valence of {context['avg_valence']}."
        )

    if context["avg_energy"] is not None:
        energy = "high-energy" if context["avg_energy"] > 0.6 else "chill"
        insights.append(
            f"You tend toward {energy} tracks (avg energy: {context['avg_energy']})."
        )

    if not insights:
        insights.append("Sync more data to unlock personalized insights!")

    for text in insights:
        session.add(Insight(
            insight_type="weekly",
            content=text,
            metadata_json=json.dumps(context),
            generated_at=datetime.utcnow(),
        ))
    session.commit()
    print(f"  Generated {len(insights)} rule-based insights.")
    return insights
