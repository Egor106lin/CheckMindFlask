from flask import Blueprint, request, jsonify, make_response, abort, g
from service.login_required import login_required
from service.update_access_token import accessTokenUpdater
from entities import User, Group

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/refresh_token', methods=['POST'])
@login_required()
def refresh_token():
    user = g.user
    if user.provider == "Google":
        new_token = accessTokenUpdater.update_google_access_token(user.access_token, user.refresh_token)
    elif user.provider == 'VK':
        new_token = accessTokenUpdater.update_vk_access_token(user.access_token, user.refresh_token)
    if not new_token:
        return abort(401)
    
    response = make_response(jsonify({"status": "ok"}))
    response.set_cookie(
        'access_token',
        new_token,
        httponly=True,
        secure=True,
        samesite='Lax',
        path='/'
    )
    return response


@profile_bp.route('/user_data', methods=['GET'])
@login_required()
def profile_user_data():
    user_data = User()
    user_data.create_with_token(request.cookies.get('access_token'))
    return jsonify({
        "name": user_data.name,
        "provider": user_data.provider,
        "avatar_url": user_data.avatar_url,
        "email": user_data.email,
        "id": user_data.id
    }), 200


@profile_bp.route('/leave', methods=['GET'])
@login_required()
def profile_leave():
    resp = make_response()
    resp.delete_cookie('access_token')
    return resp


@profile_bp.route('/delete')
@login_required()
def profile_delete():
    try:
        user = User()
        if user.create_with_token(request.cookies.get('access_token')):
            for i in user.groups_admin_of:
                group = Group()
                if group.create_with_id(i):
                    group.delete_person(user.id)
            for j in user.groups_user_of:
                group = Group()
                if group.create_with_id(j):
                    group.delete_user(user.id)
            if user.delete_from_db():
                return jsonify({
                    'status': 'success'
                }), 200
            else:
                return jsonify({
                    'status': 'error'
                }), 500
    except:
        return jsonify({
            'status': 'error'
        }), 500