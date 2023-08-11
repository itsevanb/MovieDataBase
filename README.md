
# MovieWeb App

## Overview
MovieWeb App is a web application built using Flask, SQLAlchemy, and Bootstrap. It provides a platform for users to manage profiles, interact with movies, write reviews, and explore various movie-related functionalities.

## Features

### User Management
- **Registration & Login**: Secure user registration and authentication.
- **Profile Management**: Users can view, edit, and manage their profiles, including profile pictures.
- **User Listing**: Admins can view a list of all registered users.

### Movie Interactions
- **Browse Movies**: Users can browse and view details of movies.
- **Movie Management**: Users can add, update, and delete movies.
- **Movie Reviews**: Users can write and view reviews for movies.

## Database Structure

### Users Table
- Manages user information, including one-to-one relationship with UserProfile and one-to-many with Movie and Review.

### UserProfile Table
- Contains additional profile information, such as bio and profile picture.

### Movies Table
- Stores movies associated with users, including title, description, rating, year, and poster.

### Reviews Table
- Manages reviews written by users for movies, including content and rating.

## Data Management
- **ModelsDataManager Class**: Handles CRUD operations for users, movies, and reviews using SQLAlchemy.
- **User Management**: Includes methods for adding, updating, retrieving, and deleting users and profiles.
- **Movie Management**: Provides functionality to manage movies, including adding, updating, retrieving, and deleting.
- **Review Management**: Allows creating and fetching reviews for movies.

## Structure
- `app.py`: Main entry point for the Flask application, defining routes and controllers.
- `api.py`: Defines API blueprints and routes.
- `models.py`: Contains SQLAlchemy ORM models for the database.
- `models_data_manager.py`: Class for handling database operations.

## Dependencies
- Flask
- SQLAlchemy
- Werkzeug (for security features)
- Bootstrap (for styling)

## Getting Started
1. **Setup Environment**: Create a virtual environment and install dependencies from the requirements.txt file.
2. **Database Configuration**: Set up the database connection according to the configurations in the models file.
3. **Run Application**: Execute `app.py` to start the Flask development server.
4. **Explore**: Navigate to the application in the browser to explore the features.

## Contributing
Feel free to contribute to the project by creating issues, submitting pull requests, or suggesting enhancements.

## License
Please refer to the project's license file for usage rights and limitations.
