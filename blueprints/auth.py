from flask import Blueprint, request, jsonify, redirect, abort

from service.generate_links import generate_google_url
from service.config import settings
from service.jwt_service import jwt_decode
from service.create_user import create_user

import requests

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/url/google', methods=['GET'])
def get_url_google():
    url = jsonify(generate_google_url())
    return url


@auth_bp.route('/auth/google', methods=['GET'])
def auth_google():
    try:
        data = {
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'code': request.values['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': 'http://localhost:5000/api/auth/google'
        }
        response = requests.post(
            url="https://oauth2.googleapis.com/token",
            data=data
        )
        res = response.json()
        user_data = jwt_decode(res['id_token'])
        user_data['access_token'] = res['access_token']
        user_data['token_expiry'] = res['expires_in']
        user_data['refresh_token'] = res['refresh_token']
        create_user(user_data, 'Google')
        response = redirect(f'{settings.FRONTEND_URL}/profile')
        response.set_cookie('access_token', user_data['access_token'], httponly=True)
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        return redirect(f"{settings.FRONTEND_URL}/login?error=auth_failed")