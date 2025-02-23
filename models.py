from sqlalchemy import Column, Integer, String, Table, ForeignKey, create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import ARRAY
import os

Base = declarative_base()

class Movie(Base):
    __tablename__ = 'movies'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    poster_url = Column(String)
    download_link = Column(String)
    categories = Column(ARRAY(String))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'poster_url': self.poster_url,
            'download_link': self.download_link,
            'categories': self.categories
        }

# Initialize database
def init_db():
    engine = create_engine(os.environ['DATABASE_URL'])
    Base.metadata.create_all(engine)
