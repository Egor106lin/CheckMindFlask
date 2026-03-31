from flask import Blueprint, g, request

from service.login_required import login_required
from service.response_manager import response_manager

from entities import User, Test, Group

tests_bp = Blueprint('tests', __name__)

@tests_bp.route('/created_test', methods=['POST'])
@login_required()
def test_created_test():
    try:
        data = request.get_json()
        new_test = Test()
        new_test.create_new(data)
        user = User(access_token=request.cookies.get('access_token'))
        group_with_this_test = Group(group_id=data['groupID'])
        if group_with_this_test.is_admin(user.id):
            group_with_this_test.add_test(new_test.id)
            return response_manager.success_200(message=None, data={
                "receivedData": data
            })
        else:
            return response_manager.error_403()
    except Exception as e:
        return response_manager.error_500()


@tests_bp.route('/questions_and_options', methods=['POST'])
@login_required()
def test_questions_and_options():
    try:
        request_data = request.get_json()['params']
        test_id = request_data['test_id']
        user = g.user
        test_to_send = Test(test_id)
        group_with_test = Group(group_id=test_to_send.groups[0])
        if group_with_test.is_user(user.id) and test_to_send.is_visible:
            return response_manager.success_200(message=None, data=test_to_send.to_frontend_format())
        else:
            return response_manager.error_403()
    except Exception as e:
        return response_manager.error_500()
    

@tests_bp.route('/get_groups_to_create_test', methods=['GET'])
@login_required()
def test_get_groups_to_create_test():
    try:
        user = User(access_token=request.cookies.get('access_token'))
        result = user.get_groups_for_creating_test()
        return response_manager.success_200(message=None, data={
            "groups": result
        })
    except Exception as e:
        return response_manager.error_500()


@tests_bp.route('/check_answers', methods=['POST'])
@login_required()
def test_check_answers():
    try:
        request_data = request.get_json()
        test_to_check = Test(test_id=request_data['test_id'])
        user = User(access_token=request.cookies.get('access_token'))
        return response_manager.success_200(message=None, data=test_to_check.check_answers(request_data['user_answers'], user.name))
    except Exception as e:
        print(e)
        return response_manager.error_500()
    

@tests_bp.route('/delete', methods=['POST'])
@login_required()
def test_delete():
    try:
        test_id = request.get_json()['test_id']
        test = Test(test_id)
        if test.delete_test():
            return response_manager.success_200()
        else:
            return response_manager.error_500()
    except Exception as e:
        return response_manager.error_500()


@tests_bp.route('/archive', methods=['POST'])
@login_required()
def test_archive():
    try:
        test_id = request.get_json()['test_id']
        test = Test(test_id=test_id)
        if test.archive_test():
            return response_manager.success_200()
        else:
            return response_manager.error_500()
    except Exception as e:
        return response_manager.error_500()
    

@tests_bp.route('/dearchive', methods=['POST'])
@login_required()
def test_dearchive():
    try:
        test_id = request.get_json()['test_id']
        test = Test(test_id=test_id)
        if test.dearchive_test():
            return response_manager.success_200()
        else:
            return response_manager.error_500()
    except Exception as e:
        return response_manager.error_500()