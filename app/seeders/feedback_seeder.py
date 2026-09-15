from datetime import datetime, timedelta

from app.extensions import db
from app.factories.feedback_factory import FeedbackFactory
from app.models.guest import Guest
from app.models.stay import Stay

POSITIVE_COMMENTS = [
    "The room was clean and comfortable. The staff were very helpful.",
    "Excellent stay. The staff were polite and the service was very good.",
    "Everything was well managed and the room was comfortable.",
    "The food was excellent and the service was quick.",
    "Very pleasant experience. The staff made us feel welcome.",
    "The room was spotless and the overall service was excellent.",
    "Great experience. Check-in was smooth and the staff were friendly.",
    "Very comfortable stay with excellent housekeeping.",
    "The hotel service was better than expected. We had a great stay.",
    "The staff were professional and extremely helpful.",
    "Everything was clean and well maintained.",
    "Excellent food and very good room service.",
    "The overall experience was excellent and relaxing.",
    "The hotel provided very good service throughout our stay.",
]

NEUTRAL_COMMENTS = [
    "The stay was comfortable overall, although the service was a little slow.",
    "The room was good, but the restaurant service could be improved.",
    "Overall the experience was satisfactory.",
    "The hotel was decent, although some services took longer than expected.",
    "The room was comfortable but the food quality was average.",
    "The staff were helpful, although check-in took some time.",
    "Everything was acceptable, but there is room for improvement.",
    "The stay was fine overall with a few minor issues.",
    "The service was satisfactory but not particularly impressive.",
    "The hotel was comfortable, although some facilities need improvement.",
]

NEGATIVE_COMMENTS = [
    "The room was not properly cleaned and the response from staff was delayed.",
    "The air conditioning did not work properly during the stay.",
    "The food quality was poor and the service was very slow.",
    "The room had cleanliness issues when we arrived.",
    "The Wi-Fi connection kept disconnecting and was difficult to use.",
    "The staff response to our complaint was very disappointing.",
    "Check-in took too long and the room was not ready on time.",
    "The billing amount did not match what was expected.",
    "The bathroom required maintenance and was not in good condition.",
    "The restaurant service was extremely slow.",
    "The room was noisy and the issue was not resolved quickly.",
    "We were unhappy with the overall service provided.",
]


POSITIVE_RATINGS = [
    (4.8, 4.9, 4.7, 4.8),
    (4.5, 4.7, 4.8, 4.6),
    (4.7, 4.8, 4.6, 4.7),
    (4.9, 4.8, 4.9, 4.8),
    (4.4, 4.6, 4.5, 4.7),
    (4.8, 4.7, 4.9, 4.8),
    (4.6, 4.5, 4.7, 4.6),
    (5.0, 4.8, 4.9, 4.9),
    (4.7, 4.6, 4.8, 4.7),
    (4.9, 4.9, 4.8, 4.9),
    (4.5, 4.7, 4.6, 4.5),
    (4.8, 4.8, 4.7, 4.9),
    (4.6, 4.7, 4.8, 4.6),
    (4.9, 4.8, 4.7, 4.8),
]

NEUTRAL_RATINGS = [
    (3.2, 3.4, 3.1, 3.3),
    (3.5, 3.2, 3.4, 3.3),
    (3.0, 3.4, 3.2, 3.1),
    (3.6, 3.5, 3.3, 3.4),
    (3.1, 3.2, 3.5, 3.3),
    (3.4, 3.6, 3.2, 3.5),
    (3.3, 3.1, 3.4, 3.2),
    (3.7, 3.4, 3.5, 3.3),
    (3.2, 3.5, 3.1, 3.4),
    (3.5, 3.3, 3.4, 3.2),
]

NEGATIVE_RATINGS = [
    (1.5, 2.0, 2.2, 1.8),
    (2.0, 1.8, 2.1, 1.9),
    (1.2, 1.5, 1.8, 1.4),
    (2.3, 2.1, 1.9, 2.0),
    (1.7, 2.0, 1.6, 1.8),
    (2.4, 2.2, 2.0, 2.1),
    (1.5, 1.8, 2.0, 1.7),
    (2.1, 1.9, 1.8, 2.0),
    (1.3, 1.6, 1.5, 1.7),
    (2.0, 2.2, 1.9, 2.1),
    (1.8, 1.7, 2.1, 1.9),
    (2.2, 2.0, 1.7, 1.9),
]


def seed_feedbacks():

    guests = Guest.query.order_by(Guest.id).all()
    stays = Stay.query.order_by(Stay.id).all()

    if not guests:
        raise Exception(
            "No guests found. Seed guests first."
        )

    if not stays:
        raise Exception(
            "No stays found. Seed stays first."
        )

    feedback_data = []

    for index, ratings in enumerate(POSITIVE_RATINGS):

        feedback_data.append({
            "guest": guests[index % len(guests)],
            "stay": stays[index % len(stays)],
            "cleanliness": ratings[0],
            "staff": ratings[1],
            "food": ratings[2],
            "service": ratings[3],
            "comment": POSITIVE_COMMENTS[index],
            "feedback_date": datetime.now() - timedelta(
                minutes=index * 10
            )
        })

    for index, ratings in enumerate(NEUTRAL_RATINGS):

        actual_index = index + 14

        feedback_data.append({
            "guest": guests[actual_index % len(guests)],
            "stay": stays[actual_index % len(stays)],
            "cleanliness": ratings[0],
            "staff": ratings[1],
            "food": ratings[2],
            "service": ratings[3],
            "comment": NEUTRAL_COMMENTS[index],
            "feedback_date": datetime.now() - timedelta(
                minutes=actual_index * 10
            )
        })

    for index, ratings in enumerate(NEGATIVE_RATINGS):

        actual_index = index + 24

        feedback_data.append({
            "guest": guests[actual_index % len(guests)],
            "stay": stays[actual_index % len(stays)],
            "cleanliness": ratings[0],
            "staff": ratings[1],
            "food": ratings[2],
            "service": ratings[3],
            "comment": NEGATIVE_COMMENTS[index],
            "feedback_date": datetime.now() - timedelta(
                minutes=actual_index * 10
            )
        })

    feedbacks = FeedbackFactory.create_batch(feedback_data)

    db.session.add_all(feedbacks)
    db.session.commit()

    print(
        f"{len(feedbacks)} feedback records created."
    )

    return feedbacks