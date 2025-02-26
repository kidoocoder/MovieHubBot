"""
Database Operations
This module handles all database operations for the movie database.
"""

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base, Movie
import os
from typing import Dict, List, Optional
import logging
from config import DATABASE_URL
logger = logging.getLogger(__name__)

class MovieDatabase:
    """
    Movie Database Handler

    Singleton class that handles all database operations for movies.
    Implements connection pooling and error handling.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MovieDatabase, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize database connection with connection pooling"""
        if self._initialized:
            return

        try:
            self.engine = create_engine(
                os.environ['DATABASE_URL'],
                pool_pre_ping=True,
                pool_recycle=300
            )
            Base.metadata.create_all(self.engine)
            session_factory = sessionmaker(bind=self.engine)
            self.Session = scoped_session(session_factory)
            self._initialized = True
            logger.info("Database connection initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise

    def get_session(self):
        """Get a new database session"""
        return self.Session()

    def add_movie(self, movie_data: Dict) -> bool:
        """
        Add a new movie to the database.

        Args:
            movie_data (Dict): Dictionary containing movie information

        Returns:
            bool: True if successful, False otherwise
        """
        session = self.get_session()
        try:
            movie = Movie(
                name=movie_data['name'],
                description=movie_data['description'],
                poster_url=movie_data['poster_url'],
                download_link=movie_data['download_link'],
                telegram_link=movie_data['telegram_link'],
                categories=movie_data['categories'],
                visible=movie_data.get('visible', True)  # Default to visible
            )
            session.add(movie)
            session.commit()
            logger.info(f"Successfully added movie: {movie_data['name']}")
            return True
        except Exception as e:
            logger.error(f"Error adding movie: {str(e)}")
            session.rollback()
            return False
        finally:
            session.close()

    def get_movie(self, movie_id: int) -> Optional[Dict]:
        """
        Get movie by ID.

        Args:
            movie_id (int): ID of the movie to retrieve

        Returns:
            Optional[Dict]: Movie data dictionary or None if not found
        """
        session = self.get_session()
        try:
            movie = session.query(Movie).filter(Movie.id == movie_id).first()
            return movie.to_dict() if movie else None
        except Exception as e:
            logger.error(f"Error getting movie: {str(e)}")
            return None
        finally:
            session.close()

    def search_movie(self, query: str) -> List[Dict]:
        """
        Search visible movies by name.

        Args:
            query (str): Search query string

        Returns:
            List[Dict]: List of matching movie dictionaries
        """
        session = self.get_session()
        try:
            movies = session.query(Movie).filter(
                and_(Movie.name.ilike(f"%{query}%"), Movie.visible == True)
            ).all()
            return [movie.to_dict() for movie in movies]
        except Exception as e:
            logger.error(f"Error searching movies: {str(e)}")
            return []
        finally:
            session.close()

    def get_all_movies(self, include_hidden: bool = False) -> List[Dict]:
        """
        Get all movies from database.

        Args:
            include_hidden (bool): Whether to include hidden movies

        Returns:
            List[Dict]: List of all movie dictionaries
        """
        session = self.get_session()
        try:
            query = session.query(Movie)
            if not include_hidden:
                query = query.filter(Movie.visible == True)
            movies = query.all()
            return [movie.to_dict() for movie in movies]
        except Exception as e:
            logger.error(f"Error getting all movies: {str(e)}")
            return []
        finally:
            session.close()

    def toggle_movie_visibility(self, movie_id: int) -> bool:
        """
        Toggle movie visibility.

        Args:
            movie_id (int): ID of the movie to toggle visibility

        Returns:
            bool: True if successful, False otherwise
        """
        session = self.get_session()
        try:
            movie = session.query(Movie).filter(Movie.id == movie_id).first()
            if movie:
                movie.visible = not movie.visible
                session.commit()
                logger.info(f"Successfully toggled visibility for movie ID {movie_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error toggling movie visibility: {str(e)}")
            session.rollback()
            return False
        finally:
            session.close()

    def get_movies_by_category(self, category: str) -> List[Dict]:
        """
        Get visible movies by category.

        Args:
            category (str): Category to filter by

        Returns:
            List[Dict]: List of movies in the specified category
        """
        session = self.get_session()
        try:
            movies = session.query(Movie).filter(
                and_(Movie.categories.any(category), Movie.visible == True)
            ).all()
            return [movie.to_dict() for movie in movies]
        except Exception as e:
            logger.error(f"Error getting movies by category: {str(e)}")
            return []
        finally:
            session.close()

    def delete_movie(self, movie_id: int) -> bool:
        """
        Delete a movie from database.

        Args:
            movie_id (int): ID of movie to delete

        Returns:
            bool: True if successful, False otherwise
        """
        session = self.get_session()
        try:
            movie = session.query(Movie).filter(Movie.id == movie_id).first()
            if movie:
                session.delete(movie)
                session.commit()
                logger.info(f"Successfully deleted movie with ID: {movie_id}")
                return True
            logger.warning(f"Movie with ID {movie_id} not found for deletion")
            return False
        except Exception as e:
            logger.error(f"Error deleting movie: {str(e)}")
            session.rollback()
            return False
        finally:
            session.close()
