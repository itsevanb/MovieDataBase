from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float, LargeBinary
from sqlalchemy.orm import relationship, declarative_base
import os

Base = declarative_base()

# Users Table
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    username = Column(String(50), unique=True)
    password = Column(String(1000))  # Consider hashing
    profile = relationship("UserProfile", uselist=False, backref="user")
    movies = relationship("Movie", backref="user")
    reviews = relationship("Review", back_populates="user")

# UserProfile Table
class UserProfile(Base):
    __tablename__ = 'user_profiles'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    bio = Column(String(500))
    profile_picture = Column(LargeBinary(length=2097152))  # 2 MB

# Movies Table
class Movie(Base):
    __tablename__ = 'movies'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String(255))
    description = Column(String(2048))
    rating = Column(Float)
    year = Column(Integer)
    poster = Column(String(255))
    reviews = relationship("Review", back_populates="movie")

# Review Table
class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    movie_id = Column(Integer, ForeignKey('movies.id'))
    content = Column(String(2048)) #Review Text
    rating = Column(Float) #Optional numerical rating
    user = relationship("User", back_populates="reviews")
    movie = relationship("Movie", back_populates="reviews")

# Check if we are in production (PythonAnywhere) or development (local)
environment = os.environ.get('ENV', 'development')

# Connection strings for both environments
connections = {
    'development': 'mysql+pymysql://itsevanb:hellohello123@localhost/testdata',
    'production': 'mysql+mysqldb://itsevanb:Baller85!!@itsevanb.mysql.pythonanywhere-services.com/itsevanb$first'
}

# Choose the appropriate connection string based on the environment
connection_string = connections[environment]

# Create engine
engine = create_engine(connection_string)

# Drop all existing tables
#Base.metadata.drop_all(engine)

# Create tables
#Base.metadata.create_all(engine)

# Use the inspector to get table names
"""inspector = reflection.Inspector.from_engine(engine)
tables = inspector.get_table_names()
print("Tables in the database:", tables)"""
