import json
from database import MovieDatabase
import os

def migrate_json_to_db():
    # Check if JSON file exists
    json_file = "data/movies.json"
    if not os.path.exists(json_file):
        print("No JSON file found to migrate")
        return
    
    # Read JSON data
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Create database connection
    db = MovieDatabase()
    
    # Migrate each movie
    for movie in data.get('movies', []):
        success = db.add_movie(movie)
        if success:
            print(f"Successfully migrated movie: {movie['name']}")
        else:
            print(f"Failed to migrate movie: {movie['name']}")

if __name__ == '__main__':
    migrate_json_to_db()
