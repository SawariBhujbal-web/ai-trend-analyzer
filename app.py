import streamlit as st
import pandas as pd
import plotly.express as px

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────
st.set_page_config(page_title="AI Trend Analyzer", layout="wide", page_icon="📊")

# ──────────────────────────────────────────────
# GLOBAL CSS
# ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Syne:wght@400;700;800&display=swap');

/* ── Base ── */
html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
section.main,
.main .block-container {
    background-color: #06080d !important;
    color: #cdd9e5 !important;
    font-family: 'JetBrains Mono', monospace !important;
}
[data-testid="stHeader"] {
    background-color: #06080d !important;
    border-bottom: 1px solid #161d2b;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #090d14 !important;
    border-right: 1px solid #1c2333 !important;
}
[data-testid="stSidebar"] * {
    color: #8b949e !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* ── Text inputs ── */
.stTextInput input {
    background-color: #0f1520 !important;
    border: 1px solid #222d40 !important;
    border-radius: 8px !important;
    color: #e6edf3 !important;
    font-family: 'JetBrains Mono', monospace !important;
    padding: 0.55rem 1rem !important;
    font-size: 0.85rem !important;
}
.stTextInput input:focus {
    border-color: #00d4aa !important;
    box-shadow: 0 0 0 3px rgba(0,212,170,0.12) !important;
    outline: none !important;
}
.stTextInput input::placeholder { color: #3a4455 !important; }
.stTextInput label { color: #484f58 !important; font-size: 0.72rem !important; }

/* ── Buttons ── */
.stButton > button {
    background: transparent !important;
    border: 1px solid #00d4aa55 !important;
    border-radius: 8px !important;
    color: #00d4aa !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 0.75rem !important;
    letter-spacing: 1.5px !important;
    padding: 0.5rem 1.4rem !important;
    text-transform: uppercase !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: #00d4aa14 !important;
    border-color: #00d4aa !important;
    box-shadow: 0 0 20px rgba(0,212,170,0.18) !important;
    transform: translateY(-1px) !important;
}

/* ── Metrics ── */
[data-testid="metric-container"] {
    background: linear-gradient(145deg, #0d1420, #090d14) !important;
    border: 1px solid #1c2333 !important;
    border-radius: 12px !important;
    padding: 1.2rem 1.4rem !important;
    position: relative;
    overflow: hidden;
}
[data-testid="metric-container"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #00d4aa66, transparent);
}
[data-testid="stMetricLabel"] {
    color: #484f58 !important;
    font-size: 0.68rem !important;
    letter-spacing: 1.8px !important;
    text-transform: uppercase !important;
    font-family: 'JetBrains Mono', monospace !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.9rem !important;
    font-weight: 800 !important;
    color: #e6edf3 !important;
}
[data-testid="stMetricDelta"] {
    color: #00d4aa !important;
    font-size: 0.72rem !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* ── Chart wrapper ── */
.chart-wrap {
    background: linear-gradient(145deg, #0d1420, #090d14);
    border: 1px solid #1c2333;
    border-radius: 14px;
    padding: 1.2rem 1.4rem 0.6rem;
    margin-bottom: 1.4rem;
    position: relative;
    overflow: hidden;
}
.chart-wrap::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #00d4aa44, #0066cc33, transparent);
}

/* ── DATAFRAME FIX — don't override backgrounds, just style text ── */
[data-testid="stDataFrame"] {
    border: 1px solid #1c2333 !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}
[data-testid="stDataFrame"] th {
    background-color: #0d1420 !important;
    color: #00d4aa !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid #1c2333 !important;
    padding: 0.6rem 1rem !important;
}
[data-testid="stDataFrame"] td {
    color: #cdd9e5 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important;
    border-bottom: 1px solid #111827 !important;
    padding: 0.5rem 1rem !important;
}
[data-testid="stDataFrame"] tr:hover td {
    background-color: #00d4aa08 !important;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
}

/* ── Divider ── */
hr { border-color: #161d2b !important; margin: 1.5rem 0 !important; }

/* ── Typography ── */
h1, h2, h3, h4 {
    font-family: 'Syne', sans-serif !important;
    color: #e6edf3 !important;
}

/* ── Page title ── */
.page-title {
    font-family: 'Poppins', sans-serif;
    font-size: 7rem;
    font-weight: 800;
    color: #e6edf3;
    line-height: 1.5;
    margin-top: 10px;
    margin-bottom: 10px;
}
.page-title span { color: #00d4aa; }
.page-subtitle {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: #3a4455;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 6px;
    margin-bottom: 0;
}

/* ── Section tags ── */
.sec-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #00d4aa;
    border: 1px solid #00d4aa2a;
    background: linear-gradient(135deg, #00d4aa0d, #00d4aa05);
    border-radius: 5px;
    padding: 3px 12px;
    margin-bottom: 1rem;
}

/* ── Result pill ── */
.result-pill {
    display: inline-block;
    background: #00d4aa12;
    border: 1px solid #00d4aa3a;
    color: #00d4aa;
    border-radius: 20px;
    padding: 3px 16px;
    font-size: 0.72rem;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 1rem;
    letter-spacing: 0.5px;
}

/* ── Alert banners ── */
.alert-trending {
    background: #f8514909;
    border: 1px solid #f8514930;
    border-left: 3px solid #f85149;
    border-radius: 10px;
    padding: 1rem 1.4rem;
    margin-top: 1rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    color: #f85149;
}
.alert-monitoring {
    background: #0066cc09;
    border: 1px solid #0066cc30;
    border-left: 3px solid #0066cc;
    border-radius: 10px;
    padding: 1rem 1.4rem;
    margin-top: 1rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    color: #4d9de0;
}
.alert-meta { color: #3a4455; font-size: 0.68rem; margin-top: 4px; }

/* ── Empty state ── */
.empty-state {
    background: #090d14;
    border: 1px dashed #1c2333;
    border-radius: 14px;
    padding: 3rem;
    text-align: center;
    margin-top: 1rem;
}

/* ── Sidebar brand ── */
.brand {
    font-family: 'Syne', sans-serif;
    font-size: 1.2rem;
    font-weight: 800;
    color: #e6edf3 !important;
    margin-bottom: 0;
}
.brand span { color: #00d4aa !important; }
.brand-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.58rem;
    color: #3a4455 !important;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    margin-bottom: 1.4rem;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #06080d; }
::-webkit-scrollbar-thumb { background: #1e2535; border-radius: 4px; }

/* ── Footer ── */
footer, .stCaption {
    color: #222d40 !important;
    font-family: 'JetBrains Mono', monospace !important;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# PLOTLY THEME
# ──────────────────────────────────────────────
CHART_STYLE = dict(
    paper_bgcolor="#090d14",
    plot_bgcolor="#090d14",
    font=dict(color="#cdd9e5", family="JetBrains Mono, monospace", size=11),
    margin=dict(t=52, b=44, l=16, r=16),
    
)

# ──────────────────────────────────────────────
# ANALYSIS FUNCTIONS
# Swap these with: from utils.analysis import clean_text, add_sentiment, check_trending
# ──────────────────────────────────────────────
def clean_text(df):
    if "title" in df.columns:
        df["full_text"] = df["title"].astype(str).str.lower()
    return df

def add_sentiment(df):
    import random
    sentiments = ["Positive", "Neutral", "Negative"]
    weights    = [0.45, 0.35, 0.20]
    if "sentiment" not in df.columns:
        df["sentiment"] = [random.choices(sentiments, weights)[0] for _ in range(len(df))]
    return df

def check_trending(df, keyword):
    if "full_text" not in df.columns:
        return 0
    return int(df["full_text"].str.contains(keyword.lower(), na=False).sum())

# ──────────────────────────────────────────────
# LOAD DATA
# ──────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        posts  = pd.read_csv("data/reddit_posts.csv")
        trends = pd.read_csv("data/trending_keywords.csv")
    except Exception:
        import random
        sample_titles = [
            "AI is changing everything", "Crypto market update",
            "New fashion trends 2025", "Climate change solutions",
            "Tech layoffs continue", "Mental health awareness",
            "Space exploration news", "Electric vehicle surge",
            "Social media addiction", "Remote work culture",
        ]
        posts  = pd.DataFrame({"title": sample_titles * 10})
        trends = pd.DataFrame({
            "keyword":   ["AI", "crypto", "fashion", "climate", "tech",
                          "health", "space", "EV", "social", "remote"],
            "frequency": [320, 210, 185, 160, 145, 130, 115, 98, 87, 74],
        })
    return posts, trends

posts, trends = load_data()
posts = clean_text(posts)
posts = add_sentiment(posts)

top_keyword = str(trends.iloc[0, 0]) if len(trends) else "—"

# ──────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
        <p class="brand">📊 AI <span>Trend</span></p>
        <p class="brand-sub">// analyzer · v1.0</p>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<span class="sec-tag">Navigation</span>', unsafe_allow_html=True)

    page = st.radio(
        "",
        ["📈  Overview", "🔍  Search Posts", "📡  Trend Alert"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown('<span class="sec-tag">At a Glance</span>', unsafe_allow_html=True)
    st.markdown(f"""
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;line-height:1.6">
            <div style="color:#3a4455;font-size:0.62rem;letter-spacing:1.5px;
                text-transform:uppercase;margin-bottom:2px">Posts Indexed</div>
            <div style="color:#e6edf3;font-size:1.1rem;font-family:'Syne',sans-serif;
                font-weight:800;margin-bottom:1rem">{len(posts)}</div>
            <div style="color:#3a4455;font-size:0.62rem;letter-spacing:1.5px;
                text-transform:uppercase;margin-bottom:2px">Top Keyword</div>
            <div style="color:#00d4aa;font-size:0.9rem;font-weight:600">{top_keyword}</div>
        </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
# PAGE: OVERVIEW
# ══════════════════════════════════════════════
if page == "📈  Overview":

    st.markdown("""
        <p class="page-title">AI Social Media <span>Trend Analyzer</span></p>
        <p class="page-subtitle">// reddit data · sentiment · keywords · growth</p>
    """, unsafe_allow_html=True)
    st.divider()

    # Quick Stats
    st.markdown('<span class="sec-tag">⚡ Quick Stats</span>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Posts",      len(posts))
    m2.metric("Keywords Indexed", len(trends))
    m3.metric("Top Keyword",      top_keyword)
    m4.metric("Top Frequency",    int(trends.iloc[0, 1]) if len(trends) else 0)
    st.divider()

    # Bar chart
    st.markdown('<span class="sec-tag">🔥 Trending Keywords</span>', unsafe_allow_html=True)
    top_trends = trends.sort_values(by=trends.columns[1], ascending=False).head(10)

    fig1 = px.bar(
        top_trends,
        x=top_trends.columns[0],
        y=top_trends.columns[1],
        title="Top 10 Trending Keywords",
        color=top_trends.columns[1],
        color_continuous_scale=[[0, "#112233"], [0.5, "#0055bb"], [1, "#00d4aa"]],
    )
    fig1.update_traces(marker_line_width=0, marker_cornerradius=4)
    fig1.update_coloraxes(showscale=False)
    fig1.update_layout(
        **CHART_STYLE, height=320,
        xaxis_tickangle=-35,
        xaxis=dict(title="", gridcolor="#111827", tickfont=dict(size=10)),
        yaxis=dict(title="Frequency", gridcolor="#111827", zerolinecolor="#111827"),
        title_font=dict(size=13, color="#8b949e", family="JetBrains Mono"),
    )
    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)
    st.divider()

    # Sentiment + Growth side by side
    left, right = st.columns(2)

    with left:
        st.markdown('<span class="sec-tag">💬 Sentiment</span>', unsafe_allow_html=True)
        fig2 = px.pie(
            posts, names="sentiment", title="Sentiment Distribution",
            color="sentiment",
            color_discrete_map={
                "Positive": "#00d4aa", "Neutral": "#2a3a4e", "Negative": "#f85149"
            },
            hole=0.58,
        )
        fig2.update_traces(
            textinfo="label+percent",
            textfont=dict(size=11, color="#e6edf3"),
            marker=dict(line=dict(color="#06080d", width=3)),
            pull=[0.03, 0, 0],
        )
        fig2.update_layout(
            **CHART_STYLE, height=320,
            title_font=dict(size=13, color="#8b949e", family="JetBrains Mono"),
            legend=dict(orientation="h", y=-0.18, font=dict(color="#8b949e", size=10)),
        )
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<span class="sec-tag">📈 Growth Trend</span>', unsafe_allow_html=True)
        fig3 = px.line(
            top_trends,
            x=top_trends.columns[0],
            y=top_trends.columns[1],
            title="Keyword Growth Curve",
            markers=True,
        )
        fig3.update_traces(
            line=dict(color="#00d4aa", width=2.5),
            marker=dict(color="#00d4aa", size=7, line=dict(color="#06080d", width=2)),
            fill="tozeroy",
            fillcolor="rgba(0,212,170,0.06)",
        )
        fig3.update_layout(
            **CHART_STYLE,
            xaxis=dict(title="", gridcolor="#111827", tickfont=dict(size=9), tickangle=-30),
            yaxis=dict(title="", gridcolor="#111827", zerolinecolor="#111827"),
            title_font=dict(size=13, color="#8b949e", family="JetBrains Mono"),
        )
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # Sentiment table
    st.markdown('<span class="sec-tag">🧠 Sentiment Data</span>', unsafe_allow_html=True)
    display_df = posts[["title", "sentiment"]].head(10).reset_index(drop=True)
    st.dataframe(display_df, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════
# PAGE: SEARCH POSTS
# ══════════════════════════════════════════════
elif page == "🔍  Search Posts":

    st.markdown("""
        <p class="page-title">Search <span>Posts</span></p>
        <p class="page-subtitle">// filter by keyword · sentiment aware</p>
    """, unsafe_allow_html=True)
    st.divider()

    search_word = st.text_input(
        "Search keyword",
        placeholder="e.g. AI, crypto, fashion …",
        label_visibility="visible",
    )

    if search_word:
        filtered = posts[posts["full_text"].str.contains(search_word.lower(), na=False)]

        c1, c2, c3 = st.columns(3)
        c1.metric("Matching Posts", len(filtered))
        if len(filtered):
            sc = filtered["sentiment"].value_counts()
            c2.metric("Top Sentiment", sc.index[0])
            c3.metric("Match Rate", f"{len(filtered)/len(posts)*100:.1f}%")

        st.markdown(
            f'<span class="result-pill">// {len(filtered)} results for "{search_word}"</span>',
            unsafe_allow_html=True,
        )

        if len(filtered):
            st.dataframe(
                filtered[["title", "sentiment"]].head(20).reset_index(drop=True),
                use_container_width=True,
                hide_index=True,
            )

            if len(filtered) >= 3:
                st.markdown("---")
                st.markdown('<span class="sec-tag">💬 Sentiment Breakdown</span>', unsafe_allow_html=True)
                fig_s = px.pie(
                    filtered, names="sentiment", color="sentiment",
                    color_discrete_map={
                        "Positive": "#00d4aa", "Neutral": "#2a3a4e", "Negative": "#f85149"
                    },
                    hole=0.58, title=f'Sentiment — "{search_word}"',
                )
                fig_s.update_traces(
                    textinfo="label+percent",
                    textfont=dict(size=11, color="#e6edf3"),
                    marker=dict(line=dict(color="#06080d", width=3)),
                )
                fig_s.update_layout(
                    **CHART_STYLE, 
                    title_font=dict(size=13, color="#8b949e", family="JetBrains Mono"),
                    legend=dict(orientation="h", y=-0.18, font=dict(color="#8b949e", size=10)),
                )
                st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
                st.plotly_chart(fig_s, use_container_width=True, config={"displayModeBar": False})
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info(f"No posts found for **{search_word}**. Try a different keyword.")

    else:
        st.markdown('<span class="sec-tag">All Posts Preview</span>', unsafe_allow_html=True)
        st.dataframe(
            posts[["title", "sentiment"]].head(15).reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
        )


# ══════════════════════════════════════════════
# PAGE: TREND ALERT
# ══════════════════════════════════════════════
elif page == "📡  Trend Alert":

    st.markdown("""
        <p class="page-title">Trend <span>Alert</span></p>
        <p class="page-subtitle">// real-time keyword monitoring</p>
    """, unsafe_allow_html=True)
    st.divider()

    track = st.text_input(
        "Track keyword",
        placeholder="e.g. AI, fashion, climate …",
        label_visibility="visible",
    )
    THRESHOLD = 5

    if track:
        count = check_trending(posts, track)
        delta_val = count - THRESHOLD
        st.metric(
            "Mention Count", count,
            delta=f"{'+' if delta_val >= 0 else ''}{delta_val} vs threshold",
        )

        if count >= THRESHOLD:
            st.error(f"🚨 **'{track}'** is TRENDING — {count} mentions detected!")
            st.markdown(f"""
                <div class="alert-trending">
                    ⚡ ALERT: <strong>"{track}"</strong> has exceeded the alert threshold.
                    <div class="alert-meta">
                        // Threshold: {THRESHOLD} &nbsp;·&nbsp; Detected: {count} &nbsp;·&nbsp; Status: <strong>TRENDING</strong>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            remaining = THRESHOLD - count
            st.info(f"ℹ️ **'{track}'** — {count} mentions. {remaining} more needed to trigger alert.")
            st.markdown(f"""
                <div class="alert-monitoring">
                    📡 Monitoring <strong>"{track}"</strong> — below trending threshold.
                    <div class="alert-meta">
                        // Threshold: {THRESHOLD} &nbsp;·&nbsp; Detected: {count} &nbsp;·&nbsp; Status: <strong>MONITORING</strong>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        if count > 0:
            st.divider()
            st.markdown('<span class="sec-tag">📄 Matching Posts</span>', unsafe_allow_html=True)
            filtered = posts[posts["full_text"].str.contains(track.lower(), na=False)]
            st.dataframe(
                filtered[["title", "sentiment"]].head(10).reset_index(drop=True),
                use_container_width=True,
                hide_index=True,
            )
    else:
        st.markdown("""
            <div class="empty-state">
                <p style="font-family:'Syne',sans-serif;font-size:1.3rem;color:#3a4455;margin:0">
                    Enter a keyword to begin monitoring
                </p>
                <p style="font-family:'JetBrains Mono',monospace;font-size:0.68rem;
                   color:#222d40;letter-spacing:1.5px;margin-top:0.6rem">
                    // Alert fires at 5+ mentions
                </p>
            </div>
        """, unsafe_allow_html=True)


# ──────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────
st.divider()
