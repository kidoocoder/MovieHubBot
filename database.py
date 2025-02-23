from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base, Movie
import os
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class MovieDatabase:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MovieDatabase, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize database connection"""
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
        """Get a new session"""
        return self.Session()

    def add_movie(self, movie_data: Dict) -> bool:
        """Add a new movie to the database"""
        session = self.get_session()
        try:
            movie = Movie(
                name=movie_data['name'],
                description=movie_data['description'],
                poster_url=movie_data['poster_url'],
                download_link=movie_data['download_link'],
                categories=movie_data['categories']
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
        """Get movie by ID"""
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
        """Search movies by name"""
        session = self.get_session()
        try:
            movies = session.query(Movie).filter(
                Movie.name.ilike(f"%{query}%")
            ).all()
            return [movie.to_dict() for movie in movies]
        except Exception as e:
            logger.error(f"Error searching movies: {str(e)}")
            return []
        finally:
            session.close()

    def get_all_movies(self) -> List[Dict]:
        """Get all movies"""
        session = self.get_session()
        try:
            movies = session.query(Movie).all()
            return [movie.to_dict() for movie in movies]
        except Exception as e:
            logger.error(f"Error getting all movies: {str(e)}")
            return []
        finally:
            session.close()

    def get_movies_by_category(self, category: str) -> List[Dict]:
        """Get movies by category"""
        session = self.get_session()
        try:
            movies = session.query(Movie).filter(
                Movie.categories.any(category)
            ).all()
            return [movie.to_dict() for movie in movies]
        except Exception as e:
            logger.error(f"Error getting movies by category: {str(e)}")
            return []
        finally:
            session.close()