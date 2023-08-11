from flask import Flask, redirect, render_template, request, url_for, session, Response
from api import api_blueprint 
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from movieDB.data_manager import data_manager
from movieDB.models import UserProfile, User, Movie, Review, Base, engine
import requests
import os

app = Flask(__name__)
app.register_blueprint(api_blueprint) # Register the blueprint
app.secret_key = os.environ.get('SECRET_KEY')

# Database connection string
connection_string = 'mysql+pymysql://itsevanb:hellohello123@localhost/testdata'
engine = create_engine(connection_string)
db_session = Session(engine)

"""Raise Runtime Error if SECRET_KEY is not set."""
if app.secret_key is None:
    raise RuntimeError("SECRET_KEY not set! Set the environment variable SECRET_KEY before starting the app.")

@app.route('/')
def home():
    """Render the homepage of the application."""
    return render_template('home.html')


@app.route('/users/')
def users_list():
    """Render a list of all users registered in the movie app."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    users = data_manager.get_all_users()
    return render_template('users.html', users=users)


@app.route('/users/<int:user_id>')
def user_movies(user_id):
    """Display a list of a specific user's favorite movies."""
    if user_id is None:
        return redirect(url_for('login'))
    user = data_manager.get_user(user_id)
    movies = data_manager.get_user_movies(user_id)
    return render_template('user_movies.html', movies=movies, user=user)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """Handle the form for adding a new user."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        try:
            data_manager.add_user(name)
            return redirect(url_for('users_list'))
        except Exception as e:
            print(f"An error occurred while adding a new user: {str(e)}")
            return render_template('error.html', error_message=str(e))
    return render_template('add_user.html')

@app.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        user_id = session['user_id']
        title = request.form['title'].strip()
        api_key = 'a1c766c0'
        url = f"http://www.omdbapi.com/?t={title}&apikey={api_key}&plot=full"
        try:
            response = requests.get(url)
            movie_data = response.json()
            title = movie_data.get('Title', 'Title not available')
            description = movie_data.get('Plot', 'Plot not available')
            rating = movie_data.get('imdbRating', '0.0')
            year = movie_data.get('Year', '0')
            poster = movie_data.get('Poster', 'Poster not available')
            data_manager.add_movie(user_id, title, description, rating, year, poster)
            return redirect(url_for('user_movies', user_id=user_id))
        except Exception as e:
            return render_template('error.html', error_message=str(e))
    return render_template('add_movie.html')

@app.route('/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(movie_id):
    """Handle the form for updating a movie in a user's favorites."""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    movie = data_manager.get_movie(user_id, movie_id)
    if movie is None:
        return render_template('error.html', error_message="Movie not found")
    #Check if movie belongs to the logged in user
    if movie is None or movie.user_id != user_id:
        return render_template('error.html', error_message="You are not authorized to update this movie")

    if request.method == 'POST':
        title = request.form['title']
        rating = float(request.form['rating'])
        movie.title = title
        movie.rating = rating
        try:
            data_manager.update_movie(movie)
            return redirect(url_for('user_movies', user_id=user_id))
        except Exception as e:
            print(f"An error occurred while updating a movie: {str(e)}")
            return render_template('error.html', error_message=str(e))
    else:
        return render_template('update_movie.html', movie=movie)

@app.route('/delete_movie/<int:movie_id>', methods=['POST'])
def delete_movie(movie_id):
    """Handle the form for deleting a movie from a user's favorites."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    movies = data_manager.get_user_movies(movie_id) #Get movie without filtering by user id
    movie = movies[0] if movies else None
    #Check if movie belongs to the logged in user
    if movie is None or movie.user_id != user_id:
        return render_template('error.html', error_message="You are not authorized to delete this movie")
    try:
        data_manager.delete_movie(movie_id)
        return redirect(url_for('profile', user_id=user_id))
    except Exception as e:
        print(f"An error occurred while deleting a movie: {str(e)}")
        return render_template('error.html', error_message=str(e))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle the form for registering a new user."""
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        try:
            data_manager.add_user(name, username, password)
            return redirect(url_for('login'))
        except Exception as e:
            print(f"An error occurred while adding a new user: {str(e)}")
            return render_template('error.html', error_message=str(e))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle the form for logging in a user."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = data_manager.get_all_users()
        user = next((user for user in users if user.username == username), None)
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('profile', user_id=user.id))
        else:
            return render_template('login.html', error_message='Incorrect username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Handle the form for logging out a user."""
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/profile/<int:user_id>')
def profile(user_id):
    """Display the profile page for a user."""
    if 'user_id' not in session:
        return render_template('error.html', error_message='Unauthorized access')
    user = data_manager.get_user(user_id)
    if not user:
        return render_template('error.html', error_message='User not found')
    movies = data_manager.get_user_movies(user_id)
    return render_template('profile.html', user=user, movies=movies, session=session)

UPLOAD_FOLDER = '/path/to/upload/folder'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/edit_profile/<int:user_id>', methods=['GET', 'POST'])
def edit_profile(user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        return render_template('error.html', error_message='Unauthorized access')

    user = data_manager.get_user(user_id)
    if not user:
        return render_template('error.html', error_message='User not found')

    if request.method == 'POST':
        bio = request.form['bio']
        profile_picture = request.files['profile_picture']
        profile_picture_data = None
        
        if profile_picture and allowed_file(profile_picture.filename):
            #Read files content
            profile_picture_data = profile_picture.read()

        try:
            # Update the user's data in the data source.
            data_manager.update_user_profile(user_id, bio, profile_picture_data)
            return redirect(url_for('profile', user_id=user_id))
        except Exception as e:
            return render_template('error.html', error_message=str(e))
            
    return render_template('edit_profile.html', user=user, session=session)

@app.route('/profile_picture/<int:user_id>')
def profile_picture(user_id):
    #Display user's profile picture
    user_profile = data_manager.get_user_profile(user_id)
    return Response(user_profile.profile_picture, mimetype='image/jpeg')

@app.route('/review_movie/<int:movie_id>', methods=['GET', 'POST'])
def review_movie(movie_id):
    """Handle the form for creating a review for a movie."""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    movie = data_manager.get_movie(user_id, movie_id)

    if movie is None:
        return render_template('error.html', error_message="Movie not found")

    if request.method == 'POST':
        content = request.form['content']
        rating = float(request.form['rating'])
        
        try:
            data_manager.create_review(user_id, movie_id, content, rating)  # Corrected method call
            return redirect(url_for('movie_details', movie_id=movie_id))
        except Exception as e:
            print(f"An error occurred while creating a review: {str(e)}")
            return render_template('error.html', error_message=str(e))
    else:
        return render_template('review.html', movie=movie)
    
@app.route('/movie_details/<int:movie_id>', methods=['GET'])
def movie_details(movie_id):
    """Display the details for a specific movie, including reviews."""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    movie = data_manager.get_movie(user_id, movie_id)
    reviews = data_manager.get_movie_reviews(movie_id)

    if movie is None:
        return render_template('error.html', error_message="Movie not found")

    return render_template('movie_details.html', movie=movie, reviews=reviews)

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

Base.metadata.create_all(engine)

if __name__ == '__main__':
    app.run(debug=True)