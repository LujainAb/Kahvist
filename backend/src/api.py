import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks' , methods=['GET'])
def get_drinks():
    #querying all drinks avalible in the menu DB
    drinks_query = Drink.query.all()
    #checkign if the returned result from the query is empty or not , if yes return an appropriate error
    if len(drinks_query) == 0:
        abort(404)
    #fortmatting the drinks data representation to short()
    drinks = [drink.short() for drink in drinks_query]

    return jsonify({
        "success": True,
        "drinks": drinks
    }) , 200

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail' , methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    #querying all drinks avalible in the menu DB
    drinks_query = Drink.query.all()


    #checkign if the returned result from the query is empty or not , if yes return an appropriate error
    if len(drinks_query) == 0:
        abort(404)
    
    #fortmatting the drinks data representation to long()
    drinks = [drink.long() for drink in drinks_query]

    return jsonify({
        "success": True,
        "drinks": drinks
    }) , 200


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks' , methods=['POST'])
@requires_auth('post:drinks')
def add_drinks(jwt):
    #requestoing the json body from the frontend
    body = request.get_json()


    #checkign if the returned result is empty or not , if yes return an appropriate error
    if not body:
        abort(404)
    
    #getting the values 
    DrinkTitle = body.get('title', '')

    # Refrence https://stackoverflow.com/questions/17043860/how-to-dump-a-dict-to-a-json-file
    DrinkRecipe = json.dumps(body.get('recipe')) 

    #Assigning to a drink object
    drink = Drink(
        title= DrinkTitle,
        recipe= DrinkRecipe
    )
    #using the insert method to insert it in the db 
    drink.insert()
    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    }) , 200



'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>' , methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(jwt, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    
    #checking the drink exist , if not return an appropriate error
    if (drink is None):
        abort(404)
    else:

        body = request.get_json()

    #checkign if the returned result is empty or not , if yes return an appropriate error
        if not body:
            abort(400)
    
    #getting the values 
        DrinkTitle = body.get('title', '')
        DrinkRecipe = json.dumps(body.get('recipe')) 

    #Assigning the new values
        drink.title = DrinkTitle
        drink.recipe = DrinkRecipe

    #using the update method to update it in the db 
        drink.update()
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
         }) , 200
        

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>' , methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    
    #checking the drink exist , if not return an appropriate error
    if (drink is None):
        abort(404)
    else:
        drink.delete()
        return jsonify({
            "success": True,
            "delete": drink.id
        }) , 200
        


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''


'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
        }), 404

@app.errorhandler(400)
def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'bad request'
        }), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401        

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

@app.errorhandler(AuthError)
def Auth_error(error):
    auth = jsonify(error.error)
    auth.status_code = error.status_code
    return auth

