from flask import Blueprint, request, jsonify, redirect

from service.generate_links import generate_google_url
from service.config import config
from service.jwt_service import jwt_decode
from service.create_user import create_user

import requests

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/url/google', methods=['GET'])
def get_url_google():
    state = request.args.get('state', '')
    url = jsonify(generate_google_url(state=state))
    return url


@auth_bp.route('/auth/google', methods=['GET'])
def auth_google():
    try:
        code = request.args.get('code')
        state = request.args.get('state')
        data = {
            'client_id': config.GOOGLE_CLIENT_ID,
            'client_secret': config.GOOGLE_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': config.GOOGLE_REDIRECT_URI
        }
        response = requests.post('https://oauth2.googleapis.com/token', data=data)
        res = response.json()
        user_data = jwt_decode(res['id_token'])
        user_data['access_token'] = res['access_token']
        user_data['token_expiry'] = res['expires_in']
        user_data['refresh_token'] = res['refresh_token']
        create_user(user_data, 'Google')
        redirect_target = state if state else '/'
        response = redirect(f'{config.FRONTEND_URL}{redirect_target}')
        response.set_cookie(
            'access_token',
            user_data['access_token'],
            httponly=True,
            secure=True,
            samesite='Lax',
            path='/'
        )
        return response
    except Exception as e:
        return redirect(f"{config.FRONTEND_URL}/login?error=auth_failed")