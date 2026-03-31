from flask import Blueprint, request
from entities import User, Group

from service.login_required import login_required
from service.response_manager import response_manager

groups_bp = Blueprint('groups', __name__)

@groups_bp.route('/get_list', methods=['GET'])
@login_required()
def groups_get_list():
    try:
        user = User(access_token=request.cookies.get('access_token'))
        groups_admin_of = []
        groups_user_of = []
        for i in user.groups_admin_of:
            group_to_show = Group(group_id=i)
            owner = User(user_id=group_to_show.admins[0])
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
            group_to_show = Group(group_id=k)
            owner = User(user_id=group_to_show.admins[0])
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
    
        return response_manager.success_200(
            {
                "ru-RU": "Данные успешно отправлены",
                "en-US": "The data has been sent successfully"
            },
            {
                "adminGroupsData": groups_admin_of,
                "userGroupsData": groups_user_of
            }
        )
        
    except Exception as e:
        print(f"Ошибка при обработке запроса: {e}")
        return response_manager.error_500()
    

@groups_bp.route('/get_members', methods=['POST'])
@login_required()
def groups_get_members():
    try:
        group = Group(group_id=request.get_json()['group_id'])
        user = User(access_token=request.cookies.get('access_token'))
        data = group.get_members(user.id)
        return response_manager.success_200(
            {
                "ru-RU": "Данные успешно отправлены",
                "en-US": "The data has been sent successfully"
            },
            data
        )
        
    except Exception as e:
        print(f"Ошибка при обработке запроса: {e}")
        return response_manager.error_500()
   

@groups_bp.route('/delete', methods=['POST'])
@login_required()
def delete_group():
    try:
        user = User(access_token=request.cookies.get('access_token'))
        group = Group(group_id=request.get_json())
        if group.delete_group(user.id):
            return response_manager.success_200(
                {
                    "ru-RU": "Группа успешно удалена",
                    "en-US": "The group was successfully deleted"
                }
            )
        else:
            return response_manager.error_500()
    except:
        return response_manager.error_500()


@groups_bp.route('/leave', methods=['POST'])
@login_required()
def leave_group():
    try:
        group_id = request.get_json()
        group = Group(group_id=group_id)
        user = User(access_token=request.cookies.get('access_token'))
        if group.delete_person(user.id):
            user.delete_group_from_lists(group_id)
            return response_manager.success_200(
                {
                    "ru-RU": "Группа покинута",
                    "en-US": "The group is abandoned"
                }
            )
        else:
            return response_manager.error_500()
    except:
        return response_manager.error_500()
    

@groups_bp.route('/delete_member', methods=['POST'])
@login_required()
def delete_member():
    try:
        admin = User(access_token=request.cookies.get('access_token'))
        user = User(user_id=request.get_json().get('user_id'))
        group = Group(group_id=request.get_json().get('group_id'))
        if group.is_admin(admin.id):
            if user.delete_group_from_lists(group.id) and group.delete_person(user.id):
                return response_manager.success_200(
                    {
                        "ru-RU": "Участник группы удалён",
                        "en-US": "Group member deleted"
                    }
                )
            else:
                return response_manager.error_500()
        else:
            return response_manager.error_403()
    except:
        return response_manager.error_500()
    

@groups_bp.route('/make_member_admin', methods=['POST'])
@login_required()
def make_member_admin():
    try:
        admin = User(access_token=request.cookies.get('access_token'))
        user = User(user_id=request.get_json().get('user_id'))
        group = Group(group_id=request.get_json().get('group_id'))
        if group.is_admin(admin.id):
            if user.change_group_user_admin(group.id) and group.make_user_admin(user.id):
                return response_manager.success_200(
                    {
                        "ru-RU": "Участник группы стал администратором",
                        "en-US": "The group member became an administrator"
                    }
                )
            else:
                return response_manager.error_500()
        else:
            return response_manager.error_403()
    except:
        return response_manager.error_500()


@groups_bp.route('/rename', methods=['POST'])
@login_required()
def rename_group():
    try:
        admin = User(access_token=request.cookies.get('access_token'))
        group = Group(group_id=request.get_json().get('id'))
        if group.is_admin(admin.id):
            if group.change_title(request.get_json().get('title')):
                return response_manager.success_200(
                    {
                        "ru-RU": "Группа переименована",
                        "en-US": "The group was renamed"
                    }
                )
            else:
                return response_manager.error_500()
        else:
            return response_manager.error_403()
    except:
        return response_manager.error_500()


@groups_bp.route('/create', methods=['POST'])
@login_required()
def create_group():
    try:
        group_title = request.get_json().get('group_title')
        if group_title:
            user = User(access_token=request.cookies.get('access_token'))
            group_to_create = Group()
            success, new_group_id = group_to_create.create_new(group_title, user.id)
            user.add_group_admin_of(new_group_id)
        if success:
            return response_manager.success_200(
                    {
                        "ru-RU": f"Группа '{group_title}' была создана",
                        "en-US": f"The group '{group_title}' was created"
                    }
                )
        else:
            return response_manager.error_500(
                    {
                        "ru-RU": f"Что-то пошло не так, группа '{group_title}' не была создана",
                        "en-US": f"Something went wrong, and the '{group_title}' group was not created"
                    }
                )
    except Exception as e:
        print(e)
        return response_manager.error_500()