import os
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from models import setup_db, Actor


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    CORS(app)
    setup_db(app)

    @app.route('/categories')
    def get_categories():
        # Retrieving all actors from DB
        actors = Actor.query.all()
        # Formatting categories so they can be parsed as JSON
        formatted_actors = {actor.id: actor.id for actor in actors}
        return jsonify({'categories': formatted_actors})

    return app


APP = create_app()

if __name__ == '__main__':
    APP.run(host='127.0.0.1', port=8080, debug=True)
