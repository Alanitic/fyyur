import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    CORS(app, resources={r"/*": {"origins": "*"}})
    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
    @app.after_request
    def after_request(response):
        # Allowing specific methods on CORS
        response.headers.add("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")
        return response
    '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
    @app.route('/categories')
    def get_categories():
        # Retrieving all categories from DB
        categories = Category.query.all()
        # Formatting categories so they can be parsed as JSON
        formatted_category = {category.id: category.type for category in categories}
        return jsonify({'categories': formatted_category})
    '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
    @app.route('/questions', methods=['GET'])
    def get_questions():
        # Page is being received as parameter
        page = request.args.get('page', 1, int)
        # Using SQLAlchemy paginate avoiding retrieving all questions at once
        questions = Question.query.order_by(Question.id.desc()).paginate(page, QUESTIONS_PER_PAGE, error_out=False)
        categories = Category.query.all()
        if not questions.items or not categories:
            # If page is out of index a not found status code is returned
            abort(404)
        else:
            # Formatting questions and categories so they can be parsed as JSON
            formatted_questions = [question.format() for question in questions.items]
            formatted_categories = {category.id: category.type for category in categories}
            return jsonify({
                'questions': formatted_questions,
                'total_questions': Question.query.count(),
                'categories': formatted_categories,
                'current_category': None
            })
    '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

    @app.route('/questions/<question_id>', methods=['DELETE'])
    def delete_question(question_id):
        # Getting the question to delete
        question = Question.query.get(question_id)
        if not question:
            # If no question found a not found status code is returned
            abort(404)
        # Deleting question from DB
        question.delete()
        return jsonify({
            'success': True,
        })

    '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

    @app.route('/questions', methods=['POST'])
    def create_question():
        # Data is being sent within body
        data = request.get_json()
        if not data:
            abort(400)
        # Same route and method is being used for searching a question and creating a new one
        search = data.get('searchTerm', None)
        if search:
            # Seeking question in DB as case insensitive
            questions = Question.query.filter(Question.question.ilike('%{}%'.format(search))).all()
            if not questions:
                abort(404)
            formatted_questions = [question.format() for question in questions]
            return jsonify({
                'success': True,
                'questions': formatted_questions,
                'total_questions': Question.query.count(),
                'current_category': None
            })
        else:
            # This endpoint has being called to create a new question
            question = data.get('question')
            answer = data.get('answer')
            difficulty = data.get('difficulty')
            category = data.get('category')
            # Checking there is no missing data
            if question and answer and difficulty and category:
                newQuestion = Question(
                    question=question,
                    answer=answer,
                    difficulty=difficulty,
                    category=category
                )
                newQuestion.insert()
            else:
                abort(400)
            return jsonify({
                'success': True,
            })

    '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

    '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
    @app.route('/categories/<category_id>/questions')
    def get_by_category(category_id):
        # Retrieving questions from DB based on a category ID
        questions = Question.query.filter_by(category=category_id).all()
        if not questions:
            abort(404)
        formatted_questions = [question.format() for question in questions]
        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'total_questions': len(formatted_questions),
            'current_category': category_id
        })

    '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

    @app.route('/quizzes', methods=['POST'])
    def get_quiz_quiestion():
        # Data is being sent within body
        data = request.get_json()
        formatted_question = None
        if not data:
            abort(400)
        category = data.get('quiz_category').get('id')
        previous = data.get('previous_questions')
        # If no valid category was sent, returning random question from any category
        category_exist = Category.query.with_entities(Category.id).filter_by(id=category).first() is not None
        if category_exist:
            # Verifying there are some questions left within specified category
            nquestion = Question.query.filter_by(category=category).filter(Question.id.notin_(previous)).count()
            if nquestion != 0:
                # Retrieving random question that has not been sent before
                rand = random.randrange(0, nquestion)
                question = Question.query.filter_by(category=category).filter(Question.id.notin_(previous))[rand]
                formatted_question = question.format()
        else: # No valid category was received
            # Verifying there are some questions left to return
            nquestion = Question.query.filter(Question.id.notin_(previous)).count()
            if nquestion != 0:
                # Retrieving random question that has not been sent before
                rand = random.randrange(0, nquestion)
                question = Question.query.filter(Question.id.notin_(previous))[rand]
                formatted_question = question.format()
        return jsonify({
            'question': formatted_question,
            'success': True
        })

    '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

    @app.errorhandler(404)
    def not_found(error):
        # Handling error return to be JSON format
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not found"
        }), 404

    @app.errorhandler(400)
    def not_found(error):
        # Handling error return to be JSON format
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad request"
        }), 400

    return app
