from functools import wraps
import hashlib
import os


def require_apikey(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        API_KEY_HEADER_NAME = 'x-api-key'

        if not request.headers.get(API_KEY_HEADER_NAME):
            return {"message":"auth key not found"}, 401

        expected_hashed_api_key = os.environ.get('HASHED_API_KEY')
        received_api_key = request.headers.get(API_KEY_HEADER_NAME)

        received_hashed_api_key = hash_value(received_api_key)

        if expected_hashed_api_key == received_hashed_api_key:
            return view_function(*args, **kwargs)
        else:
            return {"message":"auth failure"}, 401

    return decorated_function


def hash_value(value):
    hash_object = hashlib.sha512(bytearray(value, encoding='utf8'))
    hashed = hash_object.hexdigest()

    return hashed