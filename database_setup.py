import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

Base = declarative_base()


# User Information is stored in this class

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    image = Column(String(250))
    provider = Column(String(25))


# The albums table is created with all neccesary info stored
# in this class
class AlbumDB(Base):
    __tablename__ = 'albums'

    id = Column(Integer, primary_key=True)
    albumTitle = Column(String(250), nullable=False)
    artist = Column(String(250), nullable=False)
    coverartUrl = Column(String(450), nullable=False)
    description = Column(String(), nullable=False)
    genre = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        # Album data in proper serialized format
        return {
            'id': self.id,
            'name': self.albumTitle,
            'artist': self.artist,
            'genre': self.genre,
            'coverartUrl': self.coverartUrl,
            'description': self.description
        }
# binds to the database to add this data
engine = create_engine('sqlite:///AlbumCatalog.db')
Base.metadata.create_all(engine)
