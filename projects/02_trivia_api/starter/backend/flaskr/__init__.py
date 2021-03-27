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
        response.headers.add("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")
        return response
    '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
    @app.route('/categories')
    def get_categories():
        categories = Category.query.all()
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
        page = request.args.get('page', 1, int)
        questions = Question.query.order_by(Question.id.desc()).paginate(page, QUESTIONS_PER_PAGE, error_out=False)
        categories = Category.query.all()
        if not questions.items or not categories:
            abort(404)
        else:
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
        question = Question.query.get(question_id)
        if not question:
            abort(404)

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
        data = request.get_json()
        if not data:
            abort(400)
        search = data.get('searchTerm', None)
        if search:
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
            question = data.get('question')
            answer = data.get('answer')
            difficulty = data.get('difficulty')
            category = data.get('category')
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
        questions = Question.query.filter_by(category=category_id).all()
        if not questions:
            abort(404)
        formatted_questions = [question.format() for question in questions]
        # category = Category.query.with_entities(Category.type).filter_by(id=category_id).one_or_none()
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
        data = request.get_json()
        formatted_question = None
        if not data:
            abort(400)
        category = data.get('quiz_category').get('id')
        previous = data.get('previous_questions')
        category_exist = Category.query.with_entities(Category.id).filter_by(id=category).first() is not None
        if category_exist:
            nquestion = Question.query.filter_by(category=category).filter(Question.id.notin_(previous)).count()
            if nquestion != 0:
                rand = random.randrange(0, nquestion)
                question = Question.query.filter_by(category=category).filter(Question.id.notin_(previous))[rand]
                formatted_question = question.format()
        else:
            nquestion = Question.query.filter(Question.id.notin_(previous)).count()
            if nquestion != 0:
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
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not found"
        }), 404

    @app.errorhandler(400)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad request"
        }), 400

    return app
