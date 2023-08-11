from .models import User, UserProfile, Movie, Review
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash

class ModelsDataManager:
    """DataManager class for handling operations on SQL database using SQLAlchemy models."""

    def __init__(self, session: Session):
        self.session = session

    def get_all_users(self):
        """Return a list of all users from the database."""
        return self.session.query(User).all()

    def get_user(self, user_id):
        """Return a specific user's data based on their id."""
        return self.session.query(User).filter_by(id=user_id).first()

    def add_user(self, name, username, password):
        """Add a new user to the database along with an empty profile."""
        hashed_password = generate_password_hash(password)
        new_user = User(name=name, username=username, password=hashed_password)
        new_profile = UserProfile(user=new_user)
        self.session.add(new_user)
        self.session.add(new_profile)
        self.session.commit()

    def remove_user(self, user_id):
        """Remove a specific user from the database."""
        user_to_remove = self.session.query(User).filter_by(id=user_id).first()
        if user_to_remove:
            self.session.delete(user_to_remove)
            self.session.commit()

    def get_user_profile(self, user_id):
        """Return a user's profile based on the user id."""
        return self.session.query(UserProfile).filter_by(user_id=user_id).first()

    def update_user_profile(self, user_id, bio, profile_picture):
        profile = self.get_user_profile(user_id)
        if profile:
            profile.bio = bio
            if profile_picture:
                profile.profile_picture = profile_picture
            self.session.commit()

    def verify_user(self, username, password):
        """Verify a user's credentials (username and password)."""
        user = self.session.query(User).filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            return user
        return None

    def get_user_movies(self, user_id):
        """Return all movies of a specific user."""
        return self.session.query(Movie).filter_by(user_id=user_id).all()

    def add_movie(self, user_id, title, description, rating, year, poster):
        """Add a movie to a specific user's data."""
        new_movie = Movie(user_id=user_id, title=title, description=description, rating=rating, year=year, poster=poster)
        self.session.add(new_movie)
        self.session.commit()

    def update_movie(self, movie):
        movie_to_update = self.session.query(Movie).filter_by(id=movie.id).first()
        if movie_to_update:
            movie_to_update.title = movie.title
            movie_to_update.description = movie.description
            movie_to_update.rating = movie.rating
            movie_to_update.year = movie.year
            movie_to_update.poster = movie.poster
            self.session.commit()

    def get_movie(self, user_id, movie_id):
        return self.session.query(Movie).filter_by(user_id=user_id, id=movie_id).first()
    
    def create_review(self, user_id, movie_id, content, rating):
        #Create review object
        review = Review(user_id=user_id, movie_id=movie_id, content=content, rating=rating)
        #Add review to database
        self.session.add(review)
        #Commit changes
        self.session.commit()
        return review
    
    #Fetch review for a specific movie
    def get_movie_reviews(self, movie_id):
        return self.session.query(Review).filter_by(movie_id=movie_id).all()
        
    def delete_movie(self, movie_id):
        """Remove a specific movie."""
        movie_to_remove = self.session.query(Movie).filter_by(id=movie_id).first()
        if movie_to_remove:
            self.session.delete(movie_to_remove)
            self.session.commit()
