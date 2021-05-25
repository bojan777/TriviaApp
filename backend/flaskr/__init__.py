import sys
import os
import random
from flask import (
    Flask, 
    render_template, 
    request, 
    Response, 
    flash, 
    redirect, 
    url_for, 
    jsonify, 
    abort
)
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10



def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  CORS(app)
  setup_db(app)
  cors = CORS(app, resources={r"*/api/*": {"origins": "*"}})
  
  # CORS Headers 
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response



  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs      
  '''

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow                                 
  '''



  def get_category_list():
      categories = {}
      for category in Category.query.all():
          categories[category.id] = category.type
      return categories



  def get_questions_list():
      questions = Question.query.all()
      formatted_questions = [question.format() for question in questions]
      return formatted_questions


  '''
  @TODO: 
  Create an endpoint to handle GET requests                              
  for all available categories.
  '''


  @app.route('/categories')
  @cross_origin()
  def retrieve_categories():

    categories = get_category_list()
    if len(categories) == 0:
        abort(404)

    return jsonify({
        'success': True,
        'status': 200,
        'categories': categories
  
    })


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



  @app.route('/questions')
  @cross_origin()
  def retrieve_questions():

    try:
      questions = Question.query.all()
      categories = get_category_list()
      if len(questions) == 0:
          abort(404)

      total_questions = len(questions)
      current_questions = paginate_questions(request, questions)

      
      return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions' : total_questions,
          'categories': categories,
          'current_category': None
      })
    
    except:
      abort(422)


  '''
  @TODO:                                            
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''


  @app.route('/questions/<int:q_id>', methods=['DELETE'])
  @cross_origin()
  def delete_question(q_id):

    if not request.method == 'DELETE':
            abort(405)

    try:
      question = Question.query.filter(Question.id == q_id).one_or_none()

      if question is None:
        abort(404)

      question.delete()
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request,selection)
      
      return jsonify({
        'status': 200,
        'success': True
        })

    except:
      abort(422)


  '''
  @TODO:                                     
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''


  @app.route('/add', methods=['POST'])
  @cross_origin()
  def create_question():
    body = request.get_json()
    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    new_difficulty = body.get('difficulty', None)
    
    if not request.method == 'POST':
      abort(405)

    try:
      question = Question(question=new_question, answer=new_answer, 
                          difficulty=new_difficulty, category=new_category)
      question.insert()


      return jsonify({
        'success': True,
        'status': 200,
      })

    except Exception as e:
      print('Exception is >> ',e)
      print(sys.exc_info())
      abort(422)



  '''
  @TODO:                                     
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''


  @app.route('/questions/search', methods=['POST'])
  @cross_origin()
  def search_question():

    if not request.method == 'POST':
      abort(405)

    body = request.get_json()
    searchTerm = body.get('searchTerm', None)

    try:
      selection = Question.query.filter(Question.question.ilike("%" + searchTerm + "%")).all()
      current_questions = paginate_questions(request,selection)

      return jsonify({
        'success': True,
        'questions': current_questions,
        'current_category': None,
        'total_questions': len(selection)
      })

    except Exception as e:
      print('Exception is >> ',e)
      print(sys.exc_info())
      abort(422)



  '''
  @TODO:                                  
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  @app.route('/categories/<int:c_id>/questions')
  @cross_origin()
  def questions_by_category(c_id):

    try:
      questions = Question.query.filter_by(category=int(c_id))
      formatted_questions = [question.format() for question in questions]
      

      return jsonify({
          'success': True,
          'questions': formatted_questions,
          'total_questions': len(formatted_questions),
          'current_category': None 
      })

    except Exception as e:
      print('Exception is >> ',e)
      print(sys.exc_info())
      abort(422)




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
  @cross_origin()
  def get_quiz_question():

    if not request.method == 'POST':
      abort(405)

    body = request.get_json()
    previous_questions = body.get("previous_questions", [])
    quiz_category = body.get("quiz_category", None)
    category_id = int(quiz_category['id'])

    try:
      result_length = len(Question.query.filter(Question.category==category_id).all())
      
      if (len(previous_questions) == result_length):
        question = None
      else:
        question = random.choice(Question.query.filter(Question.category==category_id, 
                                 Question.id.notin_(previous_questions)).all()).format()

      return jsonify({
          'success': True,
          'question': question,
      })
    except Exception as e:
      print('Exception is >> ',e)
      print(sys.exc_info())
      abort(422)



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
      "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "bad request"
      }), 400

  @app.errorhandler(405)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 405,
      "message": "method not allowed"
      }), 405


  return app

    