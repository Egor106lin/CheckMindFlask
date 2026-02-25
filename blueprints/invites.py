from flask import Blueprint, request, jsonify
from entities import User, Group

from service.jwt_service import jwt_encode
from service.login_required import login_required
from service.config import config

from datetime import datetime, timedelta
import jwt

invites_bp = Blueprint('invite', __name__)


@invites_bp.route('/generate/<int:group_id>', methods=['GET'])
@login_required()
def generate_invite_url(group_id):
    group_to_change = Group()
    group_to_change.create_with_id(group_id)
    admin = User()
    admin.create_with_token(request.cookies.get('access_token'))
    if admin.id not in group_to_change.admins:
        return 403
    else:
        expire_in = timedelta(days=1)
        expire_timestamp = int((datetime.now() + expire_in).timestamp())
        invite_data = {
            'group_id': group_id,
            'exp': expire_timestamp,
            'created_by_name': admin.name,
            'created_by_email': admin.email,
            'purpose': 'group_join'
        }
        token = jwt_encode(invite_data)
        invite_url = f"{config.FRONTEND_URL}/join?token={token}"
        return jsonify({
            "status": "success",
            "invite_url": invite_url
        })


@invites_bp.route('/accept', methods=['POST'])
@login_required()
def accept_invite():
    try:
        token = request.json.get('token')
        try:
            token_data = jwt.decode(
                token,
                config.JOIN_SECRET,
                algorithms=['HS256']
            )
        except jwt.exceptions.ExpiredSignatureError:
            return jsonify({"status": "error", "message": "Срок действия приглашения истек"}), 200
        except jwt.exceptions.InvalidTokenError:
            return jsonify({"status": "error", "message": "Недействительное приглашение"}), 200
        group = Group()
        group.create_with_id(token_data['group_id'])
        user = User()
        user.create_with_token(request.cookies.get('access_token'))
        if user.id in group.users:
            return jsonify({"status": "error", "message": "Вы уже в этой группе"}), 200
        if group.is_admin(user.id):
            return jsonify({"status": "error", "message": "Вы администратор этой группы"}), 200
        if group.add_user(user) and user.add_group_user_of(group.id):
            res = {
                "title": group.title,
                "name": token_data['created_by_name'],
                "email": token_data['created_by_email']
            }
            return jsonify({
                "status": "success",
                "groupData": res
            }), 200
        else:
            return jsonify({
                "status": "error"
            }), 500
    except Exception as e:
        return jsonify({
            "status": "error"
        }), 500