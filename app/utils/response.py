from flask import jsonify

def api_response(status, statusCode, message, data=None):
    if data is None:
        data = []
    response = jsonify({
        "status": status,
        "statusCode": statusCode,
        "message": message,
        "data": data
    }), statusCode

    return response