import pandas as pd


# 🔹 Load both datasets
def load_all():
    reddit_df = pd.read_csv("data/reddit_posts.csv")
    keywords_df = pd.read_csv("data/trending_keywords.csv")

    return reddit_df, keywords_df


# 🔹 Basic summary of reddit posts
def posts_summary(df):
    return {
        "total_posts": len(df),
        "subreddits": df["subreddit"].nunique(),
        "avg_upvotes": round(df["upvotes"].mean(), 2)
    }


# 🔹 Top subreddits by number of posts
def top_subreddits(df, n=5):
    return df["subreddit"].value_counts().head(n)


# 🔹 Top trending keywords
def top_keywords(df, n=10):
    return df.sort_values(by="frequency", ascending=False).head(n)


# 🔹 Convert timestamp to readable format (optional but useful)
def convert_time(df):
    df["datetime"] = pd.to_datetime(df["timestamp"], unit='s')
    
    # ✅ ADD THESE
    df["date"] = df["datetime"].dt.date
    df["hour"] = df["datetime"].dt.hour

    return df

def keywords_summary(df):
    top_row = df.sort_values(by="frequency", ascending=False).iloc[0]

    return {
        "top_keyword": top_row["keyword"],
        "max_frequency": int(top_row["frequency"]),
        "total_keywords": len(df)
    }