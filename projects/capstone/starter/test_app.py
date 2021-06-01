import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from app import create_app
from models import setup_db
from datetime import datetime


class CastingAgency(unittest.TestCase):
    """This class represents the Casting Agency test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "capstone_test"
        self.database_path = "postgresql://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_actors(self):
        """Successfully retrieves all actors"""
        res = self.client().get('/actors')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['actors'])

    def test_post_actor(self):
        """Successfully creates a new actor"""
        sent = {'age': 25,
                'gender': "Male",
                'name': "Alan"}
        res = self.client().post('/actors', json=sent)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_update_actor(self):
        """Successfully updates actor with id 1"""
        sent = {
            'name': 'Example'
        }
        res = self.client().patch('/actors/1', json=sent)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_delete_actor(self):
        """Successfully deletes actor with id 2"""
        res = self.client().delete('actors/2')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_get_movies(self):
        """Successfully retrieves all movies"""
        res = self.client().get('/movies')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['movies'])

    def test_post_movie(self):
        """Successfully creates a new movie"""
        sent = {'title': 'Flaskman',
                'release_date': datetime.today()}
        res = self.client().post('/movies', json=sent)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_update_movie(self):
        """Successfully updates movie with id 1"""
        sent = {"title": "Example"}
        res = self.client().patch('/movies/1', json=sent)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
