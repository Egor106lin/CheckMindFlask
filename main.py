import requests

from flask import Flask, make_response, request, jsonify, abort, redirect

from flask_migrate import Migrate

from models import TestModel
from entities import User, Group, Test

from service.db_init import db
from service.generate_links import generate_google_url
from service.config import settings
from service.jwt_service import jwt_decode, jwt_encode
from service.create_user import create_user
from service.login_required import login_required

import json, jwt
from datetime import datetime, timedelta

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)
with app.app_context():
    db.create_all()


@app.route('/api/url/google', methods=['GET'])
def get_url_google():
    url = jsonify(generate_google_url())
    return url


@app.route('/api/auth/google', methods=['GET'])
async def auth_google():
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
        print(e)
        return abort(500)


@app.route('/api/invite/generate/<int:group_id>', methods=['GET'])
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
        invite_url = f"{settings.FRONTEND_URL}/join?token={token}"
        return jsonify({
            "status": "success",
            "invite_url": invite_url
        })


@app.route('/api/invite/accept', methods=['POST'])
@login_required()
def accept_invite():
    try:
        token = request.json.get('token')
        try:
            token_data = jwt.decode(
                token,
                settings.JOIN_SECRET,
                algorithms=['HS256']
            )
        except jwt.exceptions.ExpiredSignatureError:
            return jsonify({"status": "error", "message": "Срок действия приглашения истек"}), 400
        except jwt.exceptions.InvalidTokenError:
            return jsonify({"status": "error", "message": "Недействительное приглашение"}), 400
        group = Group()
        group.create_with_id(token_data['group_id'])
        user = User()
        user.create_with_token(request.cookies.get('access_token'))
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
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error"
        }), 200


@app.route('/api/tests/created_test', methods=['POST'])
@login_required()
def test_created_test():
    try:
        data = request.get_json()
        new_test = Test()
        new_test.create_new(data)
        tests = TestModel.query.all()
        group_with_this_test = Group()
        group_with_this_test.create_with_id(data['groupID'])
        group_with_this_test.add_test(new_test.id)
        return jsonify({
            "status": "success", 
            "message": "Данные успешно получены",
            "received_data": data
        }), 200
        
    except Exception as e:
        print(f"Ошибка при обработке запроса: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


@app.route('/api/tests/questions_and_options', methods=['POST'])
@login_required()
def test_questions_and_options():
    try:
        request_data = request.get_json()['params']
        test_id = request_data['test_id']
        test_to_send = Test()
        test_to_send.create_with_id(test_id)
        return jsonify({
            "status": "success", 
            "message": "Данные успешно отправлены",
            "data": test_to_send.to_frontend_format()
        }), 200
        
    except Exception as e:
        print(f"Ошибка при обработке запроса: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    

@app.route('/api/tests/get_groups_to_create_test', methods=['GET'])
@login_required()
def test_get_groups_to_create_test():
    try:
        user = User()
        if user.create_with_token(request.cookies.get('access_token')):
            result = user.get_groups_for_creating_test()
            return jsonify({
                "status": "success",
                "groups": result
            }), 200
        else:
            return jsonify({
                "status": "error"
            }), 500
    except:
        return jsonify({
            "status": "error"
        }), 500



@app.route('/api/tests/check_answers', methods=['POST'])
@login_required()
def test_check_answers():
    try:
        test_to_check = Test()
        request_data = request.get_json()
        test_to_check.create_with_id(request_data['test_id'])
        user = User()
        user.create_with_token(request.cookies.get('access_token'))
        return jsonify(test_to_check.check_answers(request_data['user_answers'], user.name)), 200
        
    except Exception as e:
        print(f"Ошибка при обработке запроса: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    

@app.route('/api/tests/delete', methods=['POST'])
@login_required()
def test_delete():
    try:
        test_id = request.get_json()['test_id']
        test = Test()
        test.create_with_id(test_id)
        if test.delete_test():
            return jsonify({
                "status": "success"
            }), 200
        else:
            return jsonify({
                "status": "error"
            }), 500
    except Exception as e:
        return jsonify({
            "status": "error"
        }), 500
    

@app.route('/api/tests/archive', methods=['POST'])
@login_required()
def test_archive():
    try:
        test_id = request.get_json()['test_id']
        test = Test()
        test.create_with_id(test_id)
        if test.archive_test():
            return jsonify({
                "status": "success"
            }), 200
        else:
            return jsonify({
                "status": "error"
            }), 500
    except Exception as e:
        return jsonify({
            "status": "error"
        }), 500
    

@app.route('/api/tests/dearchive', methods=['POST'])
@login_required()
def test_dearchive():
    try:
        test_id = request.get_json()['test_id']
        test = Test()
        test.create_with_id(test_id)
        if test.dearchive_test():
            return jsonify({
                "status": "success"
            }), 200
        else:
            return jsonify({
                "status": "error"
            }), 500
    except Exception as e:
        return jsonify({
            "status": "error"
        }), 500
    

@app.route('/api/profile/user_data', methods=['GET'])
@login_required()
def profile_user_data():
    user_data = User()
    user_data.create_with_token(request.cookies.get('access_token'))
    return json.dumps({
        "name": user_data.name,
        "provider": user_data.provider,
        "avatar_url": user_data.avatar_url,
        "email": user_data.email,
        "id": user_data.id
    })


@app.route('/api/profile/leave', methods=['GET'])
@login_required()
def profile_leave():
    resp = make_response()
    resp.delete_cookie('access_token')
    return resp


@app.route('/api/profile/delete')
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


@app.route('/api/groups/get_list', methods=['GET'])
@login_required()
def groups_get_list():
    try:
        user = User()
        user.create_with_token(request.cookies.get('access_token'))
        groups_admin_of = []
        groups_user_of = []
        for i in user.groups_admin_of:
            group_to_show = Group()
            if not group_to_show.create_with_id(i):
                continue
            owner = User()
            owner.create_with_id(group_to_show.admins[0])
            tests = group_to_show.get_test()
            res_tests = []
            for j in tests:
                res_tests.append({
                    'test_name': j.title,
                    'test_description': j.description,
                    'questions_quantity': len(j.questions),
                    'archived': not j.is_visible,
                    'id': j.id,
                    'points': j.users_max_score,
                    'attempts': j.users_attempts
                })
            groups_admin_of.append({
                'id': group_to_show.id,
                'owner': owner.name,
                'name': group_to_show.title,
                'role': 'Admin',
                'size': group_to_show.size,
                'tests': res_tests,
                'indexForFirstTest': 0,
                'indexForLastTest': 3
            })
        for k in user.groups_user_of:
            group_to_show = Group()
            group_to_show.create_with_id(k)
            owner = User()
            owner.create_with_id(group_to_show.admins[0])
            tests = group_to_show.get_test()
            res_tests = []
            for m in tests:
                if m.is_visible:
                    res_tests.append({
                        'test_name': m.title,
                        'test_description': m.description,
                        'questions_quantity': len(m.questions),
                        'id': m.id,
                        'points': m.users_max_score
                    })
            groups_user_of.append({
                'id': group_to_show.id,
                'owner': owner.name,
                'name': group_to_show.title,
                'role': 'User',
                'size': group_to_show.size,
                'tests': res_tests,
                'indexForFirstTest': 0,
                'indexForLastTest': 3
            })

        return {
            "status": "success", 
            "message": "Данные успешно отправлены",
            "adminGroupsData": groups_admin_of,
            "userGroupsData": groups_user_of
        }, 200
        
    except Exception as e:
        print(f"Ошибка при обработке запроса: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    

@app.route('/api/groups/get_members', methods=['POST'])
@login_required()
def groups_get_members():
    try:
        group, user = Group(), User()
        group.create_with_id(request.get_json()['group_id'])
        user.create_with_token(request.cookies.get('access_token'))
        data = group.get_members(user.id)
        return jsonify({
            "status": "success", 
            "message": "Данные успешно отправлены",
            "data": data
        }), 200
        
    except Exception as e:
        print(f"Ошибка при обработке запроса: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
   

@app.route('/api/groups/delete', methods=['POST'])
@login_required()
def delete_group():
    try:
        user = User()
        group = Group()
        user.create_with_token(request.cookies.get('access_token'))
        group.create_with_id(request.get_json())
        res = group.delete_group(user.id)
        if res:
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


@app.route('/api/groups/leave', methods=['POST'])
@login_required()
def leave_group():
    try:
        group_id = request.get_json()
        group, user = Group(), User()
        group.create_with_id(group_id)
        user.create_with_token(request.cookies.get('access_token'))
        if group.delete_person(user.id):
            user.delete_group_from_lists(group_id)
            return jsonify({
                "status": "success", 
                "message": "Группа покинута",
            }), 200
        else:
            return jsonify({
                'status': 'error'
            }), 500
    except:
        return jsonify({
            'status': 'error'
        }), 500
    

@app.route('/api/groups/delete_member', methods=['POST'])
@login_required()
def delete_member():
    try:
        admin, user, group = User(), User(), Group()
        admin.create_with_token(request.cookies.get('access_token'))
        user.create_with_id(request.get_json().get('user_id'))
        group.create_with_id(request.get_json().get('group_id'))
        if group.is_admin(admin.id):
            if user.delete_group_from_lists(group.id) and group.delete_person(user.id):
                return jsonify({
                    'status': 'success'
                }), 200
            else:
                return jsonify({
                'status': 'error'
            }), 500
        else:
            return jsonify({
                'status': 'error'
            }), 403
    except:
        return jsonify({
            'status': 'error'
        }), 500
    

@app.route('/api/groups/make_member_admin', methods=['POST'])
@login_required()
def make_member_admin():
    try:
        admin, user, group = User(), User(), Group()
        admin.create_with_token(request.cookies.get('access_token'))
        user.create_with_id(request.get_json().get('user_id'))
        group.create_with_id(request.get_json().get('group_id'))
        if group.is_admin(admin.id):
            if user.change_group_user_admin(group.id) and group.make_user_admin(user.id):
                return jsonify({
                    'status': 'success'
                }), 200
            else:
                return jsonify({
                'status': 'error'
            }), 500
        else:
            return jsonify({
                'status': 'error'
            }), 403
    except:
        return jsonify({
            'status': 'error'
        }), 500


@app.route('/api/groups/create', methods=['POST'])
@login_required()
def create_group():
    try:
        group_title = request.get_json().get('group_title')
        if group_title:
            user = User()
            group_to_create = Group()
            user.create_with_token(request.cookies.get('access_token'))
            success, new_group_id = group_to_create.create_new(group_title, user.id)
            user.add_group_admin_of(new_group_id)
        if success:
            return jsonify({
                "status": "success", 
                "message": f"Группа '{group_to_create.title}' создана!",
            }), 200
        else:
            return jsonify({
                "status": "danger", 
                "message": f"Группа '{group_to_create.title}' не была создана, что-то пошло не так",
            }), 200
    except Exception as e:
        print(e)
        return jsonify({
            "status": "error",
            "message": "Что-то пошло не так"
        }), 500


if __name__ == '__main__':
    app.run(debug=True)
