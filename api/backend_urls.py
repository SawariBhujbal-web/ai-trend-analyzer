"""
backend_urls.py
---------------
Central URL registry for the Reddit Trends Dashboard API.

Usage
-----
Import BASE_URL and the helper `url_for` anywhere in your project:

    from backend_urls import url_for, CHARTS, NOTIFICATIONS

    resp = requests.get(url_for(CHARTS.LIST))
    resp = requests.get(url_for(CHARTS.SINGLE, name="top_keywords"))
    resp = requests.post(url_for(NOTIFICATIONS.READ_ALL))

The constants mirror the Flask routes defined in app.py.
"""

import os
from dataclasses import dataclass
from typing import Optional

# ──────────────────────────────────────────────
# BASE
# ──────────────────────────────────────────────

BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:5000")


def url_for(path: str, **path_params: str) -> str:
    """
    Build a full URL from a path template.

    Examples:
        url_for("/api/charts/{name}", name="top_keywords")
        → "http://localhost:5000/api/charts/top_keywords"

        url_for("/api/notifications/read/{id}", id="abc123")
        → "http://localhost:5000/api/notifications/read/abc123"
    """
    resolved = path.format(**path_params) if path_params else path
    return BASE_URL.rstrip("/") + resolved


# ──────────────────────────────────────────────
# ROUTE NAMESPACES
# ──────────────────────────────────────────────

@dataclass(frozen=True)
class _DashboardRoutes:
    ROOT: str = "/"                        # GET  — HTML dashboard


@dataclass(frozen=True)
class _ChartRoutes:
    LIST: str = "/api/charts"             # GET  — list of available chart names
    SINGLE: str = "/api/charts/{name}"    # GET  — Plotly JSON for one chart
    REFRESH: str = "/api/refresh"         # POST — reload CSVs & rebuild charts


@dataclass(frozen=True)
class _NotificationRoutes:
    LIST: str = "/api/notifications"                   # GET  — all/unread notifications
    COUNT: str = "/api/notifications/count"            # GET  — {"unread": N}
    READ_ONE: str = "/api/notifications/read/{id}"     # POST — mark single as read
    READ_ALL: str = "/api/notifications/read-all"      # POST — mark all as read


DASHBOARD = _DashboardRoutes()
CHARTS = _ChartRoutes()
NOTIFICATIONS = _NotificationRoutes()


# ──────────────────────────────────────────────
# FULL URL SHORTCUTS  (no path-param substitution needed)
# ──────────────────────────────────────────────

URLS: dict[str, str] = {
    # Dashboard
    "dashboard":            url_for(DASHBOARD.ROOT),

    # Charts
    "charts_list":          url_for(CHARTS.LIST),
    "charts_refresh":       url_for(CHARTS.REFRESH),

    # Notifications
    "notifications_list":   url_for(NOTIFICATIONS.LIST),
    "notifications_unread": url_for(NOTIFICATIONS.LIST) + "?unread=1",
    "notifications_count":  url_for(NOTIFICATIONS.COUNT),
    "notifications_all_read": url_for(NOTIFICATIONS.READ_ALL),
}

# Charts that require a {name} param — resolved at call-time via url_for()
CHART_NAMES = [
    "upvotes_by_subreddit",
    "top_keywords",
    "posts_over_time",
    "subreddit_share",
    "keyword_heatmap",
    "top_posts_table",
]


# ──────────────────────────────────────────────
# CONVENIENCE BUILDERS
# ──────────────────────────────────────────────

def chart_url(name: str) -> str:
    """Return the full URL for a specific chart by name."""
    if name not in CHART_NAMES:
        raise ValueError(
            f"Unknown chart '{name}'. Valid names: {CHART_NAMES}"
        )
    return url_for(CHARTS.SINGLE, name=name)


def notification_read_url(notification_id: str) -> str:
    """Return the full URL to mark a specific notification as read."""
    return url_for(NOTIFICATIONS.READ_ONE, id=notification_id)


# ──────────────────────────────────────────────
# HTTP METHOD MAP  (useful for API docs / testing)
# ──────────────────────────────────────────────

ROUTE_METHODS: dict[str, tuple[str, str]] = {
    # (HTTP_METHOD, description)
    DASHBOARD.ROOT:             ("GET",  "Render the HTML dashboard"),
    CHARTS.LIST:                ("GET",  "List available chart names"),
    CHARTS.SINGLE:              ("GET",  "Return Plotly JSON for a chart"),
    CHARTS.REFRESH:             ("POST", "Reload CSVs and rebuild all charts"),
    NOTIFICATIONS.LIST:         ("GET",  "Return all notifications (add ?unread=1 for unread only)"),
    NOTIFICATIONS.COUNT:        ("GET",  "Return unread notification count"),
    NOTIFICATIONS.READ_ONE:     ("POST", "Mark a single notification as read"),
    NOTIFICATIONS.READ_ALL:     ("POST", "Mark all notifications as read"),
}


# ──────────────────────────────────────────────
# CLI: print all registered URLs
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\nBase URL: {BASE_URL}\n")
    print(f"{'Method':<6}  {'Path':<45}  Description")
    print("─" * 90)
    for path, (method, desc) in ROUTE_METHODS.items():
        print(f"{method:<6}  {path:<45}  {desc}")

    print("\nChart URLs:")
    for name in CHART_NAMES:
        print(f"  GET  {chart_url(name)}")

    print("\nFull URLS dict:")
    for key, full_url in URLS.items():
        print(f"  {key:<28} → {full_url}")