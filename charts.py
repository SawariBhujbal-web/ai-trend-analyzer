# utils/charts.py
# All Plotly chart functions — dark theme baked in

import plotly.graph_objects as go

# ── Shared dark theme applied to every chart ──────────────────────
_DARK = dict(
    paper_bgcolor="#0d1117",
    plot_bgcolor="#0d1117",
    font=dict(color="#e6edf3", family="monospace"),
    margin=dict(t=50, b=50, l=20, r=20),
    height=360,
)


def sentiment_chart(data):
    """Donut chart — Positive / Neutral / Negative breakdown."""
    sentiment = data["sentiment"]
    labels = list(sentiment.keys())
    values = list(sentiment.values())
    colors = ["#3fb950", "#8b949e", "#f85149"]   # green, grey, red

    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.5,
            marker=dict(colors=colors, line=dict(color="#0d1117", width=2)),
            textinfo="label+percent",
            hovertemplate="%{label}: %{value} posts<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(text="Sentiment Breakdown", font=dict(size=15)),
        showlegend=True,
        legend=dict(orientation="h", y=-0.15, font=dict(color="#c9d1d9")),
        **_DARK,
    )
    return fig


def keyword_chart(data):
    """Horizontal bar chart — top trending keywords by frequency."""
    keywords = data["keywords"]
    counts   = data["counts"]

    # Colour gradient: low = dim blue, high = bright cyan
    bar_colors = [
        f"rgba(56, {130 + int(i * 12)}, 255, 0.85)"
        for i in range(len(keywords))
    ]

    fig = go.Figure(
        go.Bar(
            x=counts,
            y=keywords,
            orientation="h",
            marker=dict(color=bar_colors),
            text=counts,
            textposition="outside",
            textfont=dict(color="#c9d1d9", size=11),
            hovertemplate="%{y}: %{x} mentions<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(text="Trending Keywords", font=dict(size=15)),
        xaxis=dict(
            title="Frequency",
            gridcolor="#21262d",
            zerolinecolor="#30363d",
        ),
        yaxis=dict(autorange="reversed", gridcolor="#21262d"),
        **_DARK,
    )
    return fig


def growth_chart(data):
    """Area line chart — daily upvote growth over available days."""
    growth = data["growth"]
    n      = len(growth)
    days   = [f"Day {i+1}" for i in range(n)]

    fig = go.Figure(
        go.Scatter(
            x=days,
            y=growth,
            mode="lines+markers",
            line=dict(color="#58a6ff", width=3),
            marker=dict(size=8, color="#1f6feb", line=dict(color="#58a6ff", width=2)),
            fill="tozeroy",
            fillcolor="rgba(88,166,255,0.12)",
            hovertemplate="%{x}: %{y:,} upvotes<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(text="Daily Upvote Growth", font=dict(size=15)),
        xaxis=dict(title="Day", gridcolor="#21262d", zerolinecolor="#30363d"),
        yaxis=dict(title="Total Upvotes", gridcolor="#21262d", zerolinecolor="#30363d"),
        **_DARK,
    )
    return fig


def subreddit_bar_chart(data):
    """Bar chart — post count per subreddit (uses posts_df)."""
    df = data.get("posts_df")
    if df is None or df.empty:
        return go.Figure()

    counts = df["subreddit"].value_counts()
    colors = ["#f78166", "#ffa657", "#3fb950", "#58a6ff"]

    fig = go.Figure(
        go.Bar(
            x=counts.index.tolist(),
            y=counts.values.tolist(),
            marker=dict(color=colors[: len(counts)]),
            hovertemplate="%{x}: %{y} posts<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(text="Posts per Subreddit", font=dict(size=15)),
        xaxis=dict(title="Subreddit", gridcolor="#21262d"),
        yaxis=dict(title="Post Count", gridcolor="#21262d", zerolinecolor="#30363d"),
        **_DARK,
    )
    return fig