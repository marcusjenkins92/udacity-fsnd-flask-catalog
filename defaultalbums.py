from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, AlbumDB, User

engine = create_engine('sqlite:///AlbumCatalog.db')

Base.metadata.bind = engine
# The DBsession creates a link with the database. Until the session.commit()
# is called all data is in a staging state just like when using Git
DBSession = sessionmaker(bind=engine)

session = DBSession()

# A default user is created here
User1 = User(name="admin", email="marcus.jenkins2013@gmail.com")
session.add(User1)
session.commit()

# Sample/default albums created here
album1 = AlbumDB(albumTitle="Astroworld",
               artist="Travis Scott",
               coverartUrl="""/static/images/travis-scott-astroworld-cover-art.png""",
               description="info", genre="Hip-Hop", user_id=1)
# uses add and commit like in Git
session.add(album1)
session.commit()

album2 = AlbumDB(albumTitle="Daytona",
               artist="Pusha T",
               coverartUrl="""/static/images/220px-Daytona_by_Pusha_T.jpg""",
               description="info", genre="Hip-Hop", user_id=1)

session.add(album2)
session.commit()

album3 = AlbumDB(albumTitle="Kids See Ghosts",
               artist="Kids See Ghosts",
               coverartUrl="""/static/images/220px-Kids_See_Ghost_Cover.jpg""",
               description="info", genre="Hip-Hop", user_id=1)
session.add(album3)
session.commit()

album4 = AlbumDB(albumTitle="Scorpion",
               artist="Drake",
               coverartUrl="""/static/images/220px-Scorpion_by_Drake.jpg""",
               description="info", genre="Hip-Hop", user_id=1)

session.add(album4)
session.commit()

album5 = AlbumDB(albumTitle="Championships",
               artist="Meek Mill",
               coverartUrl="""/static/images/meek mill_championships.jpg""",
               description="info", genre="Hip-Hop", user_id=1)
session.add(album5)
session.commit()

# once evrything is added it returns this message in the terminal
print "added Albums!"
