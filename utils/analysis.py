import re
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer

sia = SentimentIntensityAnalyzer()

# CLEAN TEXT
def clean_text(df):
    df["full_text"] = df["title"].str.lower()
    df["full_text"] = df["full_text"].apply(lambda x: re.sub(r'[^a-zA-Z0-9\s]', '', x))
    return df

# ADD SENTIMENT
def add_sentiment(df):
    def get_sentiment(text):
        score = sia.polarity_scores(text)
        if score['compound'] >= 0.05:
            return "Positive"
        elif score['compound'] <= -0.05:
            return "Negative"
        else:
            return "Neutral"

    df["sentiment"] = df["full_text"].apply(get_sentiment)
    return df

# TREND CHECK
def check_trending(df, keyword):
    matched = df[df["full_text"].str.contains(keyword.lower(), na=False)]
    return len(matched)