"""
utils/notifications.py
-----------------------
In-app notification engine for the Reddit Trends Dashboard.

Stores notifications in a thread-safe deque and persists them to
notifications.json at the project root (one level above utils/).

Import from app.py:
    from utils.notifications import push_notification, run_all_checks, get_notifications
"""

import json
import logging
import os
import threading
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional

import pandas as pd

logger = logging.getLogger(__name__)

# ── config (override via env-vars) ───────────────────────────────────────────
KEYWORD_SPIKE_THRESHOLD: int = int(os.getenv("KEYWORD_SPIKE_THRESHOLD", "8"))
POST_UPVOTE_THRESHOLD:   int = int(os.getenv("POST_UPVOTE_THRESHOLD",   "5000"))
VIRAL_THRESHOLD:         int = int(os.getenv("VIRAL_THRESHOLD",         "10000"))
MAX_NOTIFICATIONS:       int = int(os.getenv("MAX_NOTIFICATIONS",       "100"))

# notifications.json lives at project root (two levels up from here)
_PROJECT_ROOT = Path(__file__).parent.parent
NOTIFICATION_LOG: Path = _PROJECT_ROOT / "notifications.json"

NotificationLevel = Literal["info", "warning", "critical"]

_lock: threading.Lock = threading.Lock()
_queue: deque[dict]   = deque(maxlen=MAX_NOTIFICATIONS)


# ── core queue operations ─────────────────────────────────────────────────────

def _make_notification(
    title:    str,
    message:  str,
    level:    NotificationLevel = "info",
    category: str = "general",
    meta:     Optional[dict] = None,
) -> dict:
    return {
        "id":        datetime.utcnow().isoformat() + f"_{len(_queue)}",
        "timestamp": datetime.utcnow().isoformat(),
        "level":     level,
        "category":  category,
        "title":     title,
        "message":   message,
        "read":      False,
        "meta":      meta or {},
    }


def push_notification(
    title:    str,
    message:  str,
    level:    NotificationLevel = "info",
    category: str = "general",
    meta:     Optional[dict] = None,
) -> dict:
    """Add a notification to the in-memory queue (thread-safe)."""
    notif = _make_notification(title, message, level, category, meta)
    with _lock:
        _queue.appendleft(notif)
    _persist()
    logger.info("[NOTIF][%s] %s", level.upper(), title)
    return notif


def get_notifications(unread_only: bool = False) -> list[dict]:
    """Return notifications, newest first."""
    with _lock:
        items = list(_queue)
    return [n for n in items if not n["read"]] if unread_only else items


def mark_read(notification_id: str) -> bool:
    with _lock:
        for n in _queue:
            if n["id"] == notification_id:
                n["read"] = True
                return True
    return False


def mark_all_read() -> int:
    count = 0
    with _lock:
        for n in _queue:
            if not n["read"]:
                n["read"] = True
                count += 1
    return count


def clear_notifications() -> None:
    with _lock:
        _queue.clear()


def unread_count() -> int:
    with _lock:
        return sum(1 for n in _queue if not n["read"])


def _persist() -> None:
    """Write queue to notifications.json (best-effort)."""
    try:
        with _lock:
            data = list(_queue)
        with open(NOTIFICATION_LOG, "w") as f:
            json.dump(data, f, indent=2)
    except OSError as exc:
        logger.warning("Could not write notifications.json: %s", exc)


def load_from_disk() -> None:
    """Hydrate the in-memory queue from notifications.json on startup."""
    if not NOTIFICATION_LOG.exists():
        return
    try:
        with open(NOTIFICATION_LOG) as f:
            saved: list[dict] = json.load(f)
        with _lock:
            _queue.clear()
            for item in reversed(saved):   # appendleft reverses order
                _queue.appendleft(item)
        logger.info("Loaded %d notifications from disk.", len(saved))
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Could not load notifications.json: %s", exc)


# ── analysis rules ────────────────────────────────────────────────────────────

def check_keyword_spikes(keywords_df: pd.DataFrame) -> list[dict]:
    """Fire a notification for every keyword above KEYWORD_SPIKE_THRESHOLD."""
    fired = []
    spikes = keywords_df[keywords_df["frequency"] >= KEYWORD_SPIKE_THRESHOLD]
    for _, row in spikes.iterrows():
        kw   = row["keyword"]
        freq = int(row["frequency"])
        level: NotificationLevel = "critical" if freq >= 10 else "warning"
        n = push_notification(
            title    = f"🔥 Keyword spike: '{kw}'",
            message  = (
                f"'{kw}' appeared {freq}× — "
                f"above threshold ({KEYWORD_SPIKE_THRESHOLD})."
            ),
            level    = level,
            category = "keyword",
            meta     = {"keyword": kw, "frequency": freq,
                        "threshold": KEYWORD_SPIKE_THRESHOLD},
        )
        fired.append(n)
    return fired


def check_viral_posts(posts_df: pd.DataFrame) -> list[dict]:
    """Fire notifications for posts above POST_UPVOTE_THRESHOLD."""
    fired = []
    high = posts_df[posts_df["upvotes"] >= POST_UPVOTE_THRESHOLD].sort_values(
        "upvotes", ascending=False
    )
    for _, row in high.iterrows():
        upvotes = int(row["upvotes"])
        level: NotificationLevel = "critical" if upvotes >= VIRAL_THRESHOLD else "warning"
        emoji  = "🚀" if upvotes >= VIRAL_THRESHOLD else "📈"
        short  = str(row["title"])[:60] + ("…" if len(str(row["title"])) > 60 else "")
        n = push_notification(
            title    = f"{emoji} Viral post in r/{row['subreddit']}",
            message  = f'"{short}" — {upvotes:,} upvotes.',
            level    = level,
            category = "viral_post",
            meta     = {"subreddit": row["subreddit"],
                        "upvotes":   upvotes,
                        "title":     row["title"]},
        )
        fired.append(n)
    return fired


def check_subreddit_activity(posts_df: pd.DataFrame) -> list[dict]:
    """IQR-based outlier detection on post count and total upvotes per subreddit."""
    fired = []
    grouped = (
        posts_df.groupby("subreddit")
        .agg(post_count=("title", "count"), total_upvotes=("upvotes", "sum"))
        .reset_index()
    )
    for col, label in [("post_count", "posts"), ("total_upvotes", "upvotes")]:
        q75       = grouped[col].quantile(0.75)
        iqr       = q75 - grouped[col].quantile(0.25)
        threshold = q75 + 1.5 * iqr
        for _, row in grouped[grouped[col] > threshold].iterrows():
            n = push_notification(
                title    = f"📊 r/{row['subreddit']} activity surge",
                message  = (
                    f"r/{row['subreddit']} has {int(row[col]):,} {label}, "
                    f"above the outlier threshold of {threshold:,.0f}."
                ),
                level    = "info",
                category = "subreddit_activity",
                meta     = {"subreddit": row["subreddit"], "metric": col,
                            "value": int(row[col]), "threshold": round(threshold, 1)},
            )
            fired.append(n)
    return fired


def run_all_checks(
    posts_df:    pd.DataFrame,
    keywords_df: pd.DataFrame,
) -> list[dict]:
    """Run every check and return all newly fired notifications."""
    fired: list[dict] = []
    fired += check_keyword_spikes(keywords_df)
    fired += check_viral_posts(posts_df)
    fired += check_subreddit_activity(posts_df)
    return fired