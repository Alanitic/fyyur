import os
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from models import setup_db, Actor, Movie


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    CORS(app)
    setup_db(app)

    @app.route('/actors')
    def get_actors():
        # Retrieving all actors from DB
        actors = Actor.query.all()
        # Formatting actors so they can be parsed as JSON
        formatted_actors = [actor.format() for actor in actors]
        return jsonify({'actors': formatted_actors})

    @app.route('/actors', methods=['POST'])
    def post_actors():
        # Data is being sent within body
        data = request.get_json()
        if not data:
            abort(400, 'No data provided')
        name = data.get('name')
        age = data.get('age')
        gender = data.get('gender')
        if name and age and gender:
            new_actor = Actor(
                name=name,
                age=age,
                gender=gender
            )
            new_actor.insert()
        else:
            abort(400, 'Name, age and gender are required')
        return jsonify({
            'success': True,
        })

    @app.route('/actors/<actor_id>', methods=['PATCH'])
    def update_actor(actor_id):
        actor = None
        data = request.get_json()
        if not data:
            abort(400, 'No data were provided')
        name = data.get('name')
        age = data.get('age')
        gender = data.get('gender')
        if name or age or gender:
            actor = Actor.query.get(actor_id)
        else:
            abort(400, 'No data to update')
        if not actor:
            abort(404, 'No actor found with provided id')
        actor.name = name or actor.name
        actor.age = age or actor.age
        actor.gender = gender or actor.gender
        actor.update()
        formatted_actor = actor.format()
        return jsonify({
            'success': True,
            'actor': formatted_actor
        })

    @app.route('/actors/<actor_id>', methods=['DELETE'])
    def delete_actor(actor_id):
        actor = Actor.query.get(actor_id)
        if not actor:
            abort(404, 'No actor found with provided id')
        formatted_actor = actor.format()
        actor.delete()
        return jsonify({
            'success': True,
            'actor': formatted_actor
        })

    @app.route('/movies')
    def get_movies():
        # Retrieving all movies from DB
        movies = Movie.query.all()
        # Formatting movies so they can be parsed as JSON
        formatted_movies = [movie.format() for movie in movies]
        return jsonify({'movies': formatted_movies})

    @app.route('/movies', methods=['POST'])
    def post_movies():
        # Data is being sent within body
        data = request.get_json()
        if not data:
            abort(400, 'No data provided')
        title = data.get('title')
        release = data.get('release_date')
        if title and release:
            new_movie = Movie(title, release)
            new_movie.insert()
        else:
            abort(400, 'title and release date are required')
        return jsonify({
            'success': True,
        })

    @app.route('/movies/<movie_id>', methods=['PATCH'])
    def update_movie(movie_id):
        movie = None
        data = request.get_json()
        if not data:
            abort(400, 'No data were provided')
        title = data.get('title')
        release_date = data.get('release_date')
        if title or release_date:
            movie = Movie.query.get(movie_id)
        else:
            abort(400, 'No data to update')
        if not movie:
            abort(404, 'No movie found with provided id')
        movie.title = title or movie.title
        movie.releaseDate = release_date or movie.releaseDate
        movie.update()
        formatted_movie = movie.format()
        return jsonify({
            'success': True,
            'movie': formatted_movie
        })

    @app.route('/movies/<movie_id>', methods=['DELETE'])
    def delete_movie(movie_id):
        movie = Movie.query.get(movie_id)
        if not movie:
            abort(404, 'No movie found with provided id')
        formatted_movie = movie.format()
        movie.delete()
        return jsonify({
            'success': True,
            'actor': formatted_movie
        })

    @app.errorhandler(400)
    def bad_request(error):
        # Handling error return to be JSON format
        return jsonify({
            "success": False,
            "error": 400,
            "message": error.description
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        # Handling error return to be JSON format
        return jsonify({
            "success": False,
            "error": 404,
            "message": error.description
        }), 404

    return app


APP = create_app()

if __name__ == '__main__':
    APP.run(host='127.0.0.1', port=8080, debug=True)
