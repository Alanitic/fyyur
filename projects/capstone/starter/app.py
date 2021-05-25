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
            abort(400)
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
            abort(400)
        return jsonify({
            'success': True,
        })

    @app.route('/movies')
    def get_movies():
        # Retrieving all movies from DB
        movies = Movie.query.all()
        # Formatting movies so they can be parsed as JSON
        formatted_movies = [movie.format() for movie in movies]
        return jsonify({'movies': formatted_movies})

    return app


APP = create_app()

if __name__ == '__main__':
    APP.run(host='127.0.0.1', port=8080, debug=True)
