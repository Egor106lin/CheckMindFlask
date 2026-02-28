from flask import Blueprint, request, jsonify
from service.login_required import login_required
from entities import User, Group

groups_bp = Blueprint('groups', __name__)

@groups_bp.route('/get_list', methods=['GET'])
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
    

@groups_bp.route('/get_members', methods=['POST'])
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
   

@groups_bp.route('/delete', methods=['POST'])
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


@groups_bp.route('/leave', methods=['POST'])
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
    

@groups_bp.route('/delete_member', methods=['POST'])
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
    

@groups_bp.route('/make_member_admin', methods=['POST'])
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


@groups_bp.route('/rename', methods=['POST'])
@login_required()
def rename_group():
    try:
        admin, group = User(), Group()
        admin.create_with_token(request.cookies.get('access_token'))
        group.create_with_id(request.get_json().get('id'))
        if group.is_admin(admin.id):
            if group.change_title(request.get_json().get('title')):
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


@groups_bp.route('/create', methods=['POST'])
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