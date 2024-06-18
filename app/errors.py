from app import app
from flask import make_response, jsonify


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify(
        {'error': error.description if error.description else 'Bad request'}
    ), 400)


@app.errorhandler(401)
def bad_request(error):
    return make_response(jsonify(
        {'error': error.description if error.description else 'Unauthorized'}
    ), 401)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify(
        {'error': error.description if error.description else 'Not found'}
    ), 404)


@app.errorhandler(409)
def conflict(error):
    return make_response(jsonify(
        {'error': error.description if error.description else 'Conflict'}
    ), 409)


@app.errorhandler(500)
def internal_error(error):
    return make_response(jsonify(
        {'error': 'Internal server error'}
    ), 500)


@app.errorhandler(405)
def internal_error(error):
    return make_response(jsonify(
        {'error': 'Method not allowed'}
    ), 405)