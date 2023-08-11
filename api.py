from flask import Blueprint, jsonify, request
from movieDB.data_manager import data_manager

api_blueprint = Blueprint('api', __name__,)

@api_blueprint.route('/users', methods=['GET'])
def get_users():
    users = data_manager.get_all_users()
    return jsonify(users=[user.serialize() for user in users]) 

@api_blueprint.route('/users/<int:user_id>/movies', methods=['GET'])
def get_user_movies(user_id):
    movies = data_manager.get_user_movies(user_id)
    return jsonify(movies=[movie.serialize() for movie in movies])

@api_blueprint.route('/users/<int:user_id>/movies', methods=['POST'])
def add_user_movie(user_id):
    movie_data = request.json
    try:
        data_manager.add_movie(user_id, movie_data)
        return jsonify(success=True), 201
    except Exception as e:
        return jsonify(error=str(e)), 400

