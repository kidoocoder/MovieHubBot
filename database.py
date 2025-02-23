import json
import os
from typing import Dict, List, Optional

class MovieDatabase:
    def __init__(self, db_file: str = "data/movies.json"):
        self.db_file = db_file
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Create database file if it doesn't exist"""
        if not os.path.exists("data"):
            os.makedirs("data")
        if not os.path.exists(self.db_file):
            with open(self.db_file, 'w') as f:
                json.dump({"movies": []}, f)

    def _read_db(self) -> Dict:
        """Read the database file"""
        with open(self.db_file, 'r') as f:
            return json.load(f)

    def _write_db(self, data: Dict):
        """Write to the database file"""
        with open(self.db_file, 'w') as f:
            json.dump(data, f, indent=4)

    def add_movie(self, movie_data: Dict) -> bool:
        """Add a new movie to the database"""
        db = self._read_db()
        movie_data['id'] = len(db['movies']) + 1
        db['movies'].append(movie_data)
        self._write_db(db)
        return True

    def get_movie(self, movie_id: int) -> Optional[Dict]:
        """Get movie by ID"""
        db = self._read_db()
        for movie in db['movies']:
            if movie['id'] == movie_id:
                return movie
        return None

    def search_movie(self, query: str) -> List[Dict]:
        """Search movies by name"""
        db = self._read_db()
        query = query.lower()
        return [
            movie for movie in db['movies']
            if query in movie['name'].lower()
        ]

    def get_all_movies(self) -> List[Dict]:
        """Get all movies"""
        db = self._read_db()
        return db['movies']

    def get_movies_by_category(self, category: str) -> List[Dict]:
        """Get movies by category"""
        db = self._read_db()
        return [
            movie for movie in db['movies']
            if category in movie['categories']
        ]
