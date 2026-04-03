from flask import Blueprint, request
from entities import User, Group

from service.jwt_service import jwt_encode
from service.login_required import login_required
from service.config import config
from service.response_manager import response_manager
from service.exceptions import *

from datetime import datetime, timedelta
import jwt

invites_bp = Blueprint('invite', __name__)


@invites_bp.route('/generate/<int:group_id>', methods=['GET'])
@login_required()
def generate_invite_url(group_id):
    try:
        group_to_change = Group(group_id=group_id)
        admin = User(access_token=request.cookies.get('access_token'))
        if not group_to_change.is_admin(admin.id):
            return PermissionDeniedError()
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
            return response_manager.success_200(
                {
                    "ru-RU": "Ссылка успешно скопирована",
                    "en-US": "The link has been copied successfully"
                },
                {
                    "inviteUrl": invite_url
                }
            )
    except NotFoundError:
        return response_manager.error_404()
    except PermissionDeniedError:
        return response_manager.error_403()
    except:
        return response_manager.error_500()


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
            return response_manager.error_400(
                {
                    "ru-RU": "Срок действия приглашения истёк",
                    "en-US": "The invitation has expired"
                }
            )
        except jwt.exceptions.InvalidTokenError:
            return response_manager.error_400(
                {
                    "ru-RU": "Недействительное приглашение",
                    "en-US": "Invalid invitation"
                }
            )
        group = Group(group_id=token_data['group_id'])
        user = User(access_token=request.cookies.get('access_token'))
        if group.is_user(user.id):
            return response_manager.error_400(
                {
                    "ru-RU": "Вы уже состоите в этой группе",
                    "en-US": "Are you already a member of this group"
                }
            )
        elif group.is_admin(user.id):
            return response_manager.error_400(
                {
                    "ru-RU": "Вы администратор этой группы",
                    "en-US": "Are you already an admin of this group"
                }
            )
        group.add_user(user)
        user.add_group_user_of(group.id)
        res = {
            "title": group.title,
            "name": token_data['created_by_name'],
            "email": token_data['created_by_email']
        }
        return response_manager.success_200(message=None, data={
            "groupData": res
        })
    except NotFoundError:
        return response_manager.error_404()
    except ConflictError:
        return response_manager.error_500()
    except:
        return response_manager.error_500()