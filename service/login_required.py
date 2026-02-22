from flask import g, request, abort
from functools import wraps
from models import UserModel

def login_required():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            access_token = request.cookies.get('access_token')
            if not access_token:
                return abort(401)
            user = UserModel.query.filter_by(access_token=access_token).first()
            if not user:
                return abort(401)
            g.user = user
            return f(*args, **kwargs)
        return decorated_function
    return decorator