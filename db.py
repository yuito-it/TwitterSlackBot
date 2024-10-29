from sqlalchemy import select
from sqlalchemy.orm import (
    DeclarativeBase,
    sessionmaker,
    Mapped,
    mapped_column,
    Session
)
from sqlalchemy import create_engine
from os import environ

dbPassword = environ.get("DB_PASSWORD")


class Base(DeclarativeBase):
    pass


class Subscribe(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    channel: Mapped[str] = mapped_column(index=True)
    target_user: Mapped[str] = mapped_column()
    by_user: Mapped[str] = mapped_column()
    retweet: Mapped[bool] = mapped_column(default=False)
    reply: Mapped[bool] = mapped_column(default=False)


# engine = create_engine(
#     f'postgresql://twibot:{dbPassword}@db/subscribeList', echo=True)
engine = create_engine(
    f'postgresql://twibot:{dbPassword}@db/twibot', echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4 dev


def createDB():
    Base.metadata.create_all(engine)


def getDB():
    """
    Provides a database session for use in a context manager.

    This function yields a database session object and ensures that the session
    is properly closed after use, even if an exception occurs.

    Yields:
        db (SessionLocal): A database session object.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def addSubscribe(subscribe: Subscribe, session: Session):
    """
    Adds a subscription to the database and commits the transaction.

    Args:
        subscribe (Subscribe): The subscription object to be added to the database.
        session (Session): The SQLAlchemy session to use for the database transaction.

    Returns:
        None
    """
    # TODO: 4 development only

    session.add(subscribe)
    session.commit()


def listSubscribe(session: Session):
    """
    Retrieve all subscription records from the database.

    Args:
        session (Session): The SQLAlchemy session object used to interact with the database.

    Returns:
        list: A list of all subscription records fetched from the database.
    """
    stmt = select(Subscribe)
    result = session.execute(stmt)
    return result.scalars().all()


def getSubscribeById(subscribe_id, session: Session):
    """
    Retrieve a Subscribe object from the database by its ID.

    Args:
        subscribe_id (int): The ID of the Subscribe object to retrieve.
        session (Session): The SQLAlchemy session to use for the query.

    Returns:
        Subscribe: The Subscribe object with the specified ID, or None if not found.
    """
    res = session.scalar(select(Subscribe).where(Subscribe.id == subscribe_id))
    return res


def getSubscribeByUser(user, session: Session):
    """
    Retrieve all subscriptions made by a specific user.

    Args:
        user (str): The username of the user whose subscriptions are to be retrieved.
        session (Session): The SQLAlchemy session to use for the database query.

    Returns:
        list: A list of Subscribe objects representing the subscriptions made by the user.
    """
    res = session.execute(select(Subscribe).where(
        Subscribe.by_user == user)).scalars().all()
    return res


def getSubscribeByTargetUser(target_user, session: Session):
    res = session.execute(select(Subscribe).where(
        Subscribe.target_user == target_user)).scalars().all()
    return res


def getSubscribeByChannel(channel, session: Session):
    """
    Retrieve all subscriptions for a given channel.

    Args:
        channel (str): The name of the channel to filter subscriptions.
        session (Session): The SQLAlchemy session to use for the query.

    Returns:
        list: A list of Subscribe objects that match the given channel.
    """
    res = session.execute(select(Subscribe).where(
        Subscribe.channel == channel)).scalars().all()
    return res


def deleteSubscribe(subscribe_id, session: Session):
    """
    Deletes a subscription from the database by its ID.

    Args:
        subscribe_id (int): The ID of the subscription to delete.
        session (Session): The SQLAlchemy session to use for the operation.

    Returns:
        None
    """
    session.delete(getSubscribeById(subscribe_id, session))
    session.commit()


class SendedTweet(Base):
    """
    Represents a tweet that has been sent.

    Attributes:
        id (int): The primary key of the sent tweet.
        tweet_id (str): The ID of the tweet.
        channel (str): The channel through which the tweet was sent.
    """
    __tablename__ = "sended_tweets"

    id: Mapped[int] = mapped_column(primary_key=True)
    tweet_id: Mapped[str] = mapped_column(index=True)
    channel: Mapped[str] = mapped_column(index=True)


def getSendedTweetByChannel(channel, session: Session):
    """
    Retrieve all sent tweets for a specific channel from the database.

    Args:
        channel (str): The channel for which to retrieve sent tweets.
        session (Session): The SQLAlchemy session to use for the database query.

    Returns:
        list: A list of SendedTweet objects that match the specified channel.
    """
    res = session.execute(select(SendedTweet).where(
        SendedTweet.channel == channel)).scalars().all()
    return res


def getSendedTweetByTweetId(tweet_id, session: Session):
    """
    Retrieve a sent tweet from the database by its tweet ID.

    Args:
        tweet_id (int): The ID of the tweet to retrieve.
        session (Session): The SQLAlchemy session to use for the database query.

    Returns:
        SendedTweet: The SendedTweet object with the specified tweet ID, or None if not found.
    """
    res = session.scalar(select(SendedTweet).where(
        SendedTweet.tweet_id == tweet_id))
    return res


def deleteSendedTweet(tweet_id, session: Session):
    """
    Delete a sent tweet from the database.

    Args:
        tweet_id (int): The ID of the tweet to be deleted.
        session (Session): The SQLAlchemy session to use for the operation.

    Returns:
        None
    """
    tweet = getSendedTweetByTweetId(tweet_id, session)
    if tweet:
        session.delete(tweet.id)
    session.commit()


def addSendedTweet(tweet_id, channel, session: Session):
    """
    Add a sent tweet to the database.

    Args:
        tweet_id (int): The ID of the tweet that was sent.
        channel (str): The channel through which the tweet was sent.
        session (Session): The SQLAlchemy session to use for database operations.

    Returns:
        None
    """
    session.add(SendedTweet(tweet_id=tweet_id, channel=channel))
    session.commit()
