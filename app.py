from flask import Flask, redirect, render_template, request, url_for, session
from movie_web_app.datamanager.json_data_manager import JSONDataManager
import requests
from werkzeug.security import check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
data_manager = JSONDataManager('movies.json')

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
    """Handle the form for adding a new movie to a user's favorites. Pull data from the OMDB API."""
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
            print(movie_data)  # for debugging
            movie = {
                'id': len(data_manager.get_user_movies(user_id)) + 1,
                'title': movie_data.get('Title', 'Title not available'),
                'year': int(movie_data.get('Year', 0)),
                'rating': float(movie_data.get('imdbRating', 0.0)),
                'poster': movie_data.get('Poster', 'Poster not available'),
                'plot': movie_data.get('Plot', 'Plot not available')
            }
            data_manager.add_movie(user_id, movie)
            return redirect(url_for('user_movies', user_id=user_id))
        except Exception as e:
            print(f"An error occurred while adding a new movie: {str(e)}")
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

    if request.method == 'POST':
        title = request.form['title']
        rating = float(request.form['rating'])
        updated_movie = {'id': movie_id, 'title': title, 'rating': rating}
        try:
            data_manager.update_movie(user_id, movie_id, updated_movie)
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
    try:
        data_manager.delete_movie(user_id, movie_id)
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
        user = next((user for user in users if 'username' in user and user['username'] == username), None)
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect(url_for('profile', user_id=user['id']))
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
    if 'user_id' not in session or session['user_id'] != user_id:
        return render_template('error.html', error_message='Unauthorized access')
    user = data_manager.get_user(user_id)
    if not user:
        return render_template('error.html', error_message='User not found')
    movies = data_manager.get_user_movies(user_id)
    return render_template('profile.html', user=user, movies=movies, session=session)

@app.route('/edit_profile/<int:user_id>', methods=['GET', 'POST'])
def edit_profile(user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        return render_template('error.html', error_message='Unauthorized access')

    user = data_manager.get_user(user_id)
    if not user:
        return render_template('error.html', error_message='User not found')

    if request.method == 'POST':
        username = request.form['username']
        bio = request.form['bio']
        try:
            # Update the user's data in the data source.
            user['username'] = username
            user['bio'] = bio
            data_manager.update_user(user_id, user)
            return redirect(url_for('profile', user_id=user_id))
        except Exception as e:
            return render_template('error.html', error_message=str(e))
            
    return render_template('edit_profile.html', user=user, session=session)


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)