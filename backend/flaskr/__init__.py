import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories")
    def retrieve_categories():
        selection = Category.query.order_by(Category.id).all()
        current_categories = [category.format() for category in selection]

        if len(current_categories) == 0:
            abort(404)

        category_dict = {} 
        
        # Loop to add key-value pair to dictionary
        for category in current_categories:
            
            if category['id'] not in category_dict:

                category_dict[category['id']] = category['type']

        return jsonify(
            {
                "success": True,
                "categories": category_dict,
                "total_categories": len(Category.query.all()),
            }
        )

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route("/questions")
    def retrieve_questions():

        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        category_selection = Category.query.order_by(Category.id).all()
        current_categories = [category.format() for category in category_selection]

        body = request.get_json()

        if body:
            current_category = body.get("quiz_category", None)
        else:
            current_category = None

        if len(current_questions) == 0:
            abort(404)

        category_dict = {} 
        
        # Loop to add key-value pair to dictionary
        for category in current_categories:

            if category['id'] not in category_dict:

                category_dict[category['id']] = category['type']

        return jsonify(
            {
                "success": True,
                "questions": current_questions,
                "total_questions": len(Question.query.all()),
                "categories": category_dict,
                "current_category": current_category,
            }
        )

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify(
                {
                    "success": True,
                    "deleted": int(question_id),
                    "questions": current_questions,
                    "total_questions": len(Question.query.all()),
                }
            )

        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route("/questions", methods=["POST"])
    def create_book():
        body = request.get_json()
       
        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        new_category = body.get("category", None)
        new_difficulty = body.get("difficulty", None)
        search = body.get("searchTerm", None)

        if body:
            current_category = body.get("quiz_category", None)
        else:
            current_category = None

        try:
            if search:
                selection = Question.query.order_by(Question.id).filter(
                    Question.question.ilike("%{}%".format(search))
                )
                current_questions = paginate_questions(request, selection)

                return jsonify(
                    {
                        "success": True,
                        "questions": current_questions,
                        "total_questions": len(selection.all()),
                        "current_category" : current_category, 
                    }
                )

            else:
                question = Question(question=new_question, answer=new_answer, category=new_category, difficulty = new_difficulty)
                question.insert()

                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)

                return jsonify(
                    {
                        "success": True,
                        "created": int(question.id),
                        "questions": current_questions,
                        "total_questions": len(Question.query.all()),
                        
                    }
                )

        except:
            abort(422)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:category_id>/questions")
    def get_category_questions(category_id):
        print(category_id)
        selection = Question.query.order_by(Question.id).filter(
                    Question.category == category_id)
        print(selection)
        current_questions = paginate_questions(request, selection)

        if len(current_questions) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "questions": current_questions,
                "total_questions": len(current_questions),
            }
        )

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route("/quizzes", methods=["POST"])
    def quiz_questions():
        body = request.get_json()

        previous_questions = body.get("previous_questions", None)
        category = body.get("quiz_category", None)

        print(previous_questions)
        print(category)

        if category == 'All':
            
            selection = Question.query.order_by(Question.id).all()
            question_choices =[]

            for question in selection:
                if question.id not in previous_questions:
                    question_choices.append(question)

            random_question = random.choice(question_choices)
            previous_questions.append(random_question.id)
            print(random_question.id)

            if random_question == None:
                abort(404)

            return jsonify(
                {
                    "success": True,
                    "previous_questions": previous_questions,
                    "question": {
                        "question": random_question.question,
                        "answer": random_question.answer,
                        "category": random_question.category,
                        "difficulty":random_question.difficulty
                    },
                    "current_category": category,
                }
            )
        
        else:

            selection = Question.query.order_by(Question.id).all()
            question_choices =[]

            for question in selection:
                if question.id not in previous_questions:
                    question_choices.append(question)

            random_question = random.choice(question_choices)
            previous_questions.append(random_question.id)
            print(random_question.id)

            if random_question == None:
                abort(404)

            return jsonify(
                {
                    "success": True,
                    "previous_questions": previous_questions,
                    "question": {
                        "question": random_question.question,
                        "answer": random_question.answer,
                        "category": random_question.category,
                        "difficulty":random_question.difficulty
                    },
                    "current_category": category,
                }
            )

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify({"success": False, "error": 400, "message": "bad request"}), 
            400,
        )

    @app.errorhandler(405)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 405, "message": "method not allowed"}),
            405,
        )

    return app

