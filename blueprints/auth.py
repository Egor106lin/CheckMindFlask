from flask import Blueprint, request, jsonify, redirect

from service.generate_links import generate_google_url, generate_vk_url
from service.config import config
from service.jwt_service import jwt_decode
from service.create_user import create_user
from service.response_manager import response_manager

import requests

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/url/google', methods=['GET'])
def get_url_google():
    state = request.args.get('state', '')
    url = jsonify(generate_google_url(state=state))
    return url


@auth_bp.route('/url/vk', methods=['GET'])
def get_url_vk():
    state = request.args.get('state', '')
    code_challenge = request.args.get('code_challenge')
    if not code_challenge:
        return response_manager.error_400({
            "ru-RU": "Нет нужного кода",
            "en-US": "Missing code"
        })
    url = generate_vk_url(code_challenge=code_challenge, state=state)
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
    except:
        return redirect(f"{config.FRONTEND_URL}/login?error=auth_failed")
    

@auth_bp.route('/auth/vk', methods=['GET'])
def auth_vk_callback():
    code = request.args.get('code')
    state = request.args.get('state')
    device_id = request.args.get('device_id')
    frontend_redirect_url = f"{config.FRONTEND_URL}/vk/callback?code={code}&state={state}&device_id={device_id}"
    return redirect(frontend_redirect_url)

@auth_bp.route('/auth/vk/exchange', methods=['POST'])
def exchange_vk_code():
    try:
        data = request.get_json()
        code = data.get('code')
        device_id = data.get('device_id')
        code_verifier = data.get('code_verifier')
        state = data.get('state')
        if not all([code, device_id, code_verifier]):
            return jsonify({"error": "Missing code, device_id, or code_verifier"}), 400
        token_data = {
            'client_id': config.VK_CLIENT_ID,
            'client_secret': config.VK_CLIENT_SECRET,
            'code': code,
            'code_verifier': code_verifier,
            'device_id': device_id,
            'grant_type': 'authorization_code',
            'redirect_uri': config.VK_REDIRECT_URI
        }
        token_response = requests.post('https://id.vk.ru/oauth2/auth', data=token_data)
        token_response.raise_for_status()
        tokens = token_response.json()
        access_token = tokens['access_token']
        refresh_token = tokens.get('refresh_token')
        expires_in = tokens.get('expires_in')
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {'client_id': config.VK_CLIENT_ID}
        userinfo_response = requests.get('https://id.vk.ru/oauth2/user_info', headers=headers, params=params)
        userinfo_response.raise_for_status()
        user_info = userinfo_response.json()['user']
        user_data = {
            'sub': user_info.get('user_id'),
            'email': user_info.get('email'),
            'name': user_info.get('first_name') + ' ' + user_info.get('last_name'),
            'picture': user_info.get('avatar'),
            'access_token': access_token,
            'refresh_token': refresh_token,
            'device_id': device_id,
            'token_expiry': expires_in
        }
        create_user(user_data, 'VK')
        response = jsonify({"success": True, "redirect": state or '/'})
        response.set_cookie(
            'access_token',
            access_token,
            httponly=True,
            secure=True,
            samesite='Lax',
            path='/'
        )
        return response

    except requests.exceptions.RequestException:
        return response_manager.error_500()
    except:
        return response_manager.error_500()