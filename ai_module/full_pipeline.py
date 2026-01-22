
# ==============================
# Secure Intelligent Feedback AI
# Author: Hackathon Team Member 3
# Features:
# - Sentiment Analysis
# - Topic Detection
# - Trend Analysis
# - Recommendations
# - Chatbot-ready Summaries
# - Top Issues Detection
# ==============================

from textblob import TextBlob
import pandas as pd
from collections import Counter

# ------------------------------
# 1️⃣ Sentiment Analysis
# ------------------------------
def analyze_sentiment(text):
    """
    Returns sentiment label and polarity score
    """
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity

    if polarity > 0.1:
        label = "Positive"
    elif polarity < -0.1:
        label = "Negative"
    else:
        label = "Neutral"

    return {"sentiment": label, "score": polarity}


# ------------------------------
# 2️⃣ Topic Detection
# ------------------------------
def extract_topics(text):
    """
    Converts feedback into academic topics
    """
    text = text.lower()
    topic_keywords = {
        "Teaching Quality": ["teacher", "teaching", "faculty", "explain", "lecture"],
        "Assessment & Exams": ["exam", "test", "assignment", "grading", "marks"],
        "Infrastructure": ["classroom", "projector", "wifi", "hostel", "canteen"],
        "Laboratory": ["lab", "equipment", "computer", "practical"],
        "Curriculum": ["syllabus", "course", "content", "subject"]
    }

    detected_topics = []
    for topic, keywords in topic_keywords.items():
        for word in keywords:
            if word in text:
                detected_topics.append(topic)
                break
    if not detected_topics:
        detected_topics.append("General Feedback")

    return detected_topics


# ------------------------------
# 3️⃣ Trend Analysis
# ------------------------------
def analyze_trends(data):
    """
    Aggregates multiple feedbacks to calculate trends and topic frequency
    """
    df = pd.DataFrame(data)
    if df.empty:
        return {"message": "No data available"}

    # Convert date
    df["date"] = pd.to_datetime(df["date"])

    # Monthly sentiment trend
    monthly_trend = (
        df.groupby(pd.Grouper(key="date", freq="ME"))["sentiment_score"]
        .mean()
        .round(2)
        .to_dict()
    )

    # Topic frequency
    topic_counts = Counter()
    for topics in df["topics"]:
        for t in topics:
            topic_counts[t] += 1

    # Top 3 issues
    top_issues = topic_counts.most_common(3)

    # Average sentiment
    avg_sentiment = round(df["sentiment_score"].mean(), 2)

    return {
        "monthly_sentiment_trend": monthly_trend,
        "topic_distribution": dict(topic_counts),
        "top_issues": top_issues,
        "average_sentiment": avg_sentiment
    }


# ------------------------------
# 4️⃣ Recommendations Engine
# ------------------------------
def generate_recommendations(trend_data):
    recommendations = []

    monthly = trend_data.get("monthly_sentiment_trend", {})
    if monthly:
        last_value = list(monthly.values())[-1]

        if last_value < 0:
            recommendations.append(
                "Overall student sentiment is declining. Review teaching and assessment practices."
            )
        elif last_value < 0.2:
            recommendations.append(
                "Student sentiment is neutral. Consider incremental improvements in delivery."
            )
        else:
            recommendations.append(
                "Student sentiment is positive. Maintain current practices."
            )

    for topic, count in trend_data.get("topic_distribution", {}).items():
        if count >= 2:
            recommendations.append(f"High volume of feedback on {topic}. Focused intervention advised.")

    if not recommendations:
        recommendations.append("Insufficient data for recommendations.")

    return recommendations


# ------------------------------
# 5️⃣ Chatbot-ready Summary
# ------------------------------
def chatbot_summary(feedback_records):
    """
    Aggregates multiple feedbacks into chatbot-friendly summary
    """
    # Run sentiment + topics per feedback
    for record in feedback_records:
        record["sentiment_score"] = analyze_sentiment(record["comment"])["score"]
        record["topics"] = extract_topics(record["comment"])

    trends = analyze_trends(feedback_records)
    recommendations = generate_recommendations(trends)

    summary = {
        "feedback_count": len(feedback_records),
        "average_sentiment": trends.get("average_sentiment"),
        "top_issues": trends.get("top_issues"),
        "recommendations": recommendations
    }

    return summary


# ------------------------------
# 6️⃣ Test / Demo Run
# ------------------------------
if __name__ == "__main__":
    sample_feedback = [
        {"date": "2024-01-15", "comment": "The teacher explains concepts clearly."},
        {"date": "2024-02-10", "comment": "Lab equipment is outdated and exams are too hard."},
        {"date": "2024-02-20", "comment": "The classroom wifi is slow, but teaching is okay."}
    ]

    result = chatbot_summary(sample_feedback)
    import pprint
    pprint.pprint(result)