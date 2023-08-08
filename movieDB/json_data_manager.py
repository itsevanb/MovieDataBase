import json
from .data_manager_interface import DataManagerInterface
from werkzeug.security import generate_password_hash, check_password_hash

class JSONDataManager(DataManagerInterface):
    """DataManager class for handling operations on JSON data."""

    def __init__(self, file_name):
        """Initialize the JSONDataManager class with the JSON file name."""
        self.file_name = 'movie_web_app/datamanager/' + file_name

    def _read_data(self):
        """Read data from the JSON file and return as a list."""
        try:
            with open(self.file_name, 'r') as file:
                return json.load(file)
        except Exception as e:
            print(f"An error occurred while reading the data: {str(e)}")
            return []

    def _write_data(self, data):
        """Write the provided data to the JSON file."""
        try:
            with open(self.file_name, 'w') as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            print(f"An error occurred while writing the data: {str(e)}")

    def get_all_users(self):
        """Return a list of all users from the JSON data."""
        return self._read_data()

    def get_user(self, user_id):
        """Return a specific user's data based on their id."""
        users = self._read_data()
        return next((user for user in users if user['id'] == user_id), None)

    def get_user_movies(self, user_id):
        """Return all movies of a specific user."""
        users = self.get_all_users()
        for user in users:
            if user['id'] == user_id:
                return user.get('movies', [])
        print(f"User with id {user_id} not found.")
        return []

    def add_user(self, name, username, password):
        """Add a new user to the JSON data."""
        try:
            users = self._read_data()
            new_user_id = max([user['id'] for user in users], default = 0) + 1
            hashed_password = generate_password_hash(password)
            new_user = {'id': new_user_id, 'name': name, 'username': username, 'password': hashed_password, 'bio': '', 'movies': []}
            users.append(new_user)
            self._write_data(users)
        except Exception as e:
            print(f"An error occurred while adding the user: {str(e)}")

    def remove_user(self, user_id):
        """Remove a specific user from the JSON data."""
        users = self.get_all_users()
        users = [user for user in users if user['id'] != user_id]
        self._write_data(users)

    def update_user(self, user_id, updated_user):
        """Update a specific user's data."""
        users = self.get_all_users()
        for i, user in enumerate(users):
            if user['id'] == user_id:
                users[i] = updated_user
                self._write_data(users)
                break

    def add_movie(self, user_id, movie):
        """Add a movie to a specific user's data."""
        users = self.get_all_users()
        for user in users:
            if user['id'] == user_id:
                user['movies'].append(movie)
        self._write_data(users)

    def update_movie(self, user_id, movie_id, updated_movie):
        """Update a specific movie of a specific user."""
        data = self._read_data()
        for user in data:
            if user['id'] == user_id:
                for movie in user['movies']:
                    if movie['id'] == movie_id:
                        movie.update(updated_movie)
                        break
        self._write_data(data)

    def get_movie(self, user_id, movie_id):
        """Return a specific movie of a specific user based on its id."""
        users = self._read_data()
        for user in users:
            if user['id'] == user_id:
                for movie in user['movies']:
                    if movie['id'] == movie_id:
                        return movie
        return None

    def delete_movie(self, user_id, movie_id):
        """Remove a specific movie of a specific user."""
        users = self.get_all_users()
        for user in users:
            if user['id'] == user_id:
                user['movies'] = [movie for movie in user['movies'] if int(movie['id']) != int(movie_id)]
        self._write_data(users)

    def verify_user(self, username, password):
        """Verify a user's credentials (username and password)."""
        users = self._read_data()
        for user in users:
            if user['username'] == username and check_password_hash(user['password'], password):
                return user
        return None