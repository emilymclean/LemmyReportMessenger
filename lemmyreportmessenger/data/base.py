from contextlib import contextmanager

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Engine, Column, INTEGER
from sqlalchemy.orm import sessionmaker, Session

from .content_type import ContentType

Base = declarative_base()
metadata = Base.metadata

engine: Engine = create_engine('sqlite:///data/database.db', echo=False)
session_maker = sessionmaker(bind=engine)


@contextmanager
def session_scope() -> Session:
    """Provide a transactional scope around a series of operations."""
    session = session_maker()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


class Report(Base):
    __tablename__ = 'report'

    report_id = Column(INTEGER, primary_key=True)
    report_type = Column(sqlalchemy.Enum(ContentType), primary_key=True)
    community_id = Column(INTEGER)


Base.metadata.create_all(engine)
