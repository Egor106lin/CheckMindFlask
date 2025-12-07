from flask import request, abort
from service.update_access_token import update_access_token
from functools import wraps
from models import UserModel

def login_required():
    def decorator(function):
        @wraps(function)
        def decorated_function(*args, **kwargs):
            try:
                access_token = request.cookies.get('access_token')
                user = UserModel.query.filter(UserModel.access_token == str(access_token)).first()
                if user:
                    update_access_token(user.access_token, user.refresh_token)
                else:
                    return abort(401)
            except Exception as e:
                return abort(401)
            return function(*args, **kwargs)
        return decorated_function
    return decorator