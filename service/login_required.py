from flask import request, abort, make_response
from service.update_access_token import update_access_token
from functools import wraps
from models import UserModel

def login_required():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                access_token = request.cookies.get('access_token')
                if not access_token:
                    return abort(401)

                user = UserModel.query.filter_by(access_token=access_token).first()
                if not user:
                    return abort(401)
                new_token = update_access_token(user.access_token, user.refresh_token)
                if new_token:
                    token_updated = True
                else:
                    token_updated = False
                response = f(*args, **kwargs)
                if not isinstance(response, tuple) and not hasattr(response, 'set_cookie'):
                    response = make_response(response)

                if token_updated:
                    response.set_cookie(
                        'access_token',
                        new_token,
                        httponly=True,
                        secure=True,
                        samesite='Lax',
                        path='/'
                    )
                return response

            except Exception as e:
                return abort(401)
        return decorated_function
    return decorator