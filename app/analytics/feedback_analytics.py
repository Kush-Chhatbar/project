import pandas as pd
import numpy as np
from textblob import TextBlob

from app.models.feedback import Feedback

class FeedbackAnalytics:

    @staticmethod
    def get_feedback_dataframe():
        feedbacks = Feedback.query.all()
        data = [
            {
                "id": feedback.id,
                "overall_rating": float(feedback.overall_rating),
                "cleanliness_rating": float(feedback.cleanliness_rating),
                "staff_rating": float(feedback.staff_rating),
                "food_rating": float(feedback.food_rating),
                "service_rating": float(feedback.service_rating),
                "comment": feedback.comment
            }
            for feedback in feedbacks
        ]
        return pd.DataFrame(data)

    # Analyze sentiment of the comments function
    @staticmethod
    def analyze_sentiment(comment):
        if pd.isna(comment) or not isinstance(comment, str):
            return "Neutral"

        comment = comment.strip()

        if not comment:
            return "Neutral"

        polarity = TextBlob(comment).sentiment.polarity

        if polarity > 0:
            return "Positive"
        if polarity < 0:
            return "Negative"

        return "Neutral"


    # Rating distribution calculation function
    @staticmethod
    def get_rating_distribution(df):
        distribution = (df["overall_rating"].round().value_counts())
        return {
            "5 Star": int(distribution.get(5, 0)),
            "4 Star": int(distribution.get(4, 0)),
            "3 Star": int(distribution.get(3, 0)),
            "2 Star": int(distribution.get(2, 0)),
            "1 Star": int(distribution.get(1, 0))
        }

    # Feedback data analytics function
    @staticmethod
    def get_analytics():
        df = FeedbackAnalytics.get_feedback_dataframe()
        if df.empty:
            return {
                "total_feedback": 0,
                "average_overall_rating": 0,
                "average_cleanliness_rating": 0,
                "average_staff_rating": 0,
                "average_food_rating": 0,
                "average_service_rating": 0,
                "positive_percentage": 0,
                "neutral_percentage": 0,
                "negative_percentage": 0,
                "rating_distribution": {}
            }

        df["sentiment"] = df["comment"].apply(FeedbackAnalytics.analyze_sentiment)
        total_feedback = len(df)
        average_overall = df["overall_rating"].mean()
        average_cleanliness = (df["cleanliness_rating"].mean())
        average_staff = (df["staff_rating"].mean())
        average_food = (df["food_rating"].mean())
        average_service = (df["service_rating"].mean())
        rating_distribution = (FeedbackAnalytics.get_rating_distribution(df))
        sentiment_counts = (df["sentiment"].value_counts())
        positive_count = sentiment_counts.get("Positive", 0)
        neutral_count = sentiment_counts.get("Neutral", 0)
        negative_count = sentiment_counts.get("Negative", 0)
        positive_percentage = (positive_count / total_feedback) * 100
        neutral_percentage = (neutral_count / total_feedback) * 100
        negative_percentage = (negative_count / total_feedback) * 100

        return {
            "total_feedback": total_feedback,
            "average_overall_rating": round(average_overall, 1),
            "average_cleanliness_rating": round(average_cleanliness, 1),
            "average_staff_rating": round(average_staff, 1),
            "average_food_rating": round(average_food, 1),
            "average_service_rating": round(average_service, 1),
            "positive_percentage": round(positive_percentage, 2),
            "neutral_percentage": round(neutral_percentage, 2),
            "negative_percentage": round(negative_percentage, 2),
            "rating_distribution": rating_distribution
        }

    # Get feedback trend analytics function (daily, weekly, monthly, yearly) based on provided filter function.
    @staticmethod
    @staticmethod
    def get_feedback_trend(period="monthly"):

        feedbacks = Feedback.query.all()

        data = [
            {
                "feedback_date": feedback.feedback_date,
                "overall_rating": float(feedback.overall_rating)
            }
            for feedback in feedbacks
            if feedback.feedback_date is not None
        ]

        if not data:
            return {
                "period": period,
                "trend": [],
                "trend_direction": "Stable",
                "change": 0
            }

        df = pd.DataFrame(data)

        df["feedback_date"] = pd.to_datetime(
            df["feedback_date"]
        )

        # Daily
        if period == "daily":

            df["period"] = (
                df["feedback_date"]
                .dt.strftime("%B %d, %Y")
            )

            df["period_sort"] = (
                df["feedback_date"].dt.normalize()
            )

        # Weekly
        elif period == "weekly":

            df["week_start"] = (
                df["feedback_date"]
                .dt.to_period("W")
                .apply(lambda x: x.start_time)
            )

            df["week_end"] = (
                df["feedback_date"]
                .dt.to_period("W")
                .apply(lambda x: x.end_time)
            )

            df["period"] = (
                df["week_start"].dt.strftime("%b %d")
                + " - "
                + df["week_end"].dt.strftime("%b %d, %Y")
            )

            df["period_sort"] = df["week_start"]

        # Monthly
        elif period == "monthly":

            df["period"] = (
                df["feedback_date"]
                .dt.strftime("%B")
            )

            df["period_sort"] = (
                df["feedback_date"].dt.month
            )

        # Yearly
        elif period == "yearly":

            df["period"] = (
                df["feedback_date"]
                .dt.strftime("%Y")
            )

            df["period_sort"] = (
                df["feedback_date"].dt.year
            )

        else:

            raise ValueError(
                "Invalid period. "
                "Supported periods: daily, weekly, monthly, yearly"
            )

        # Calculate average rating for each period
        trend = (
            df.groupby(
                ["period", "period_sort"],
                as_index=False
            )["overall_rating"]
            .mean()
            .round(2)
            .rename(
                columns={
                    "overall_rating": "average_rating"
                }
            )
            .sort_values("period_sort")
        )

        # Calculate change between latest and previous period
        if len(trend) >= 2:

            first_rating = trend.iloc[0]["average_rating"]
            latest_rating = trend.iloc[-1]["average_rating"]

            change = round(
                latest_rating - first_rating,
                2
            )

            x = np.arange(len(trend))
            y = trend["average_rating"].values

            slope = np.polyfit(x, y, 1)[0]

            if slope > 0.01:
                trend_direction = "Improving"

            elif slope < -0.01:
                trend_direction = "Declining"

            else:
                trend_direction = "Stable"

        else:

            trend_direction = "Stable"
            change = 0

        # Remove sorting column from API response
        trend = trend[
            ["period", "average_rating"]
        ]

        return {
            "period": period,
            "trend": trend.to_dict(
                orient="records"
            ),
            "trend_direction": trend_direction,
            "change": change
        }