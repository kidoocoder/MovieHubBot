"""
Movie Database Models
This module defines the SQLAlchemy models for the movie database.
"""

from sqlalchemy import Column, Integer, String, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import ARRAY
import os

DATABASE_URL = "postgres://kfcdtwea:jxgqtvc1ji7lSMjAhUp0QbxrE8Ut0t7N@fanny.db.elephantsql.com/kfcdtwea"

Base = declarative_base()

class Movie(Base):
    """
    Movie Model

    Represents a movie in the database with its associated metadata.

    Attributes:
        id (int): Unique identifier for the movie
        name (str): Name of the movie
        description (str): Description or synopsis of the movie
        poster_url (str): URL to the movie's poster image
        download_link (str): Direct download link for the movie
        telegram_link (str): Telegram channel link for movie download
        categories (list): List of categories the movie belongs to
        visible (bool): Whether the movie is visible to users (default True)
    """
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    poster_url = Column(String)
    download_link = Column(String)
    telegram_link = Column(String)
    categories = Column(ARRAY(String))
    visible = Column(Boolean, default=True)  # New field

    def to_dict(self) -> dict:
        """
        Convert movie object to dictionary representation.

        Returns:
            dict: Dictionary containing movie data
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'poster_url': self.poster_url,
            'download_link': self.download_link,
            'telegram_link': self.telegram_link,
            'categories': self.categories,
            'visible': self.visible
        }

def init_db():
    """Initialize database connection and create tables"""
    engine = create_engine(
        os.environ['DATABASE_URL'],
        pool_pre_ping=True,
        pool_recycle=300
    )
    Base.metadata.create_all(engine)
