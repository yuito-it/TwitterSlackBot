from sqlalchemy.orm import (
    DeclarativeBase,
    sessionmaker,
    Mapped,
    mapped_column,
    Session
)
from sqlalchemy import create_engine, select
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
    repliy: Mapped[bool] = mapped_column(default=False)


engine = create_engine(
    f'postgresql://twibot:{dbPassword}@db/subscribeList', echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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
    # TODO: 4 development only
    Base.metadata.create_all(engine)

    session.add(subscribe)
    session.commit()


def listSubscribe(session: Session):
    stmt = select(Subscribe)
    result = session.execute(stmt)
    return result.fetchall()


def getSubscribeById(subscribe_id, session: Session):
    res = session.scalar(select(Subscribe).where(Subscribe.id == subscribe_id))
    return res


def getSubscribeByUser(user, session: Session):
    res = session.execute(select(Subscribe).where(
        Subscribe.by_user == user)).fetchall()
    return res


def getSubscribeByChannel(channel, session: Session):
    res = session.execute(select(Subscribe).where(
        Subscribe.channel == channel)).fetchall()
    return res


def deleteSubscribe(subscribe_id, session: Session):
    session.delete(getSubscribeById(subscribe_id, session))
    session.commit()


# TODO: すでに配信済みのツイートを排他する構造を構築する
