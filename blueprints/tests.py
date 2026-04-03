from flask import Blueprint, g, request

from service.login_required import login_required
from service.response_manager import response_manager
from service.exceptions import *

from entities import User, Test, Group

tests_bp = Blueprint('tests', __name__)


@tests_bp.route('/created_test', methods=['POST'])
@login_required()
def test_created_test():
    try:
        data = request.get_json()
        if not data:
            raise ValidationError()
        new_test = Test()
        new_test.create_new(data)
        user = User(access_token=request.cookies.get('access_token'))
        group_id = data.get('groupID')
        if not group_id:
            raise ValidationError()
        group = Group(group_id=group_id)
        if not group.is_admin(user.id):
            raise PermissionDeniedError()
        group.add_test(new_test.id)
        return response_manager.success_200(message=None, data={
                "receivedData": data
            }
        )
    except ValidationError:
        return response_manager.error_400()
    except NotFoundError:
        return response_manager.error_404()
    except PermissionDeniedError:
        return response_manager.error_403()
    except (ConflictError, DatabaseError):
        return response_manager.error_500()
    except Exception:
        return response_manager.error_500()


@tests_bp.route('/questions_and_options', methods=['POST'])
@login_required()
def test_questions_and_options():
    try:
        request_data = request.get_json()
        if not request_data or 'params' not in request_data or 'test_id' not in request_data['params']:
            raise ValidationError()
        test_id = request_data['params']['test_id']
        user = g.user
        test = Test(test_id=test_id)
        group_id = test.groups[0]
        group = Group(group_id=group_id)
        if not (group.is_user(user.id) and test.is_visible):
            raise PermissionDeniedError()
        return response_manager.success_200(
            message=None,
            data=test.to_frontend_format()
        )
    except ValidationError:
        return response_manager.error_400()
    except NotFoundError:
        return response_manager.error_404()
    except Exception:
        return response_manager.error_500()


@tests_bp.route('/get_groups_to_create_test', methods=['GET'])
@login_required()
def test_get_groups_to_create_test():
    try:
        user = User(access_token=request.cookies.get('access_token'))
        result = user.get_groups_for_creating_test()
        return response_manager.success_200(message=None, data={
                "groups": result
            }
        )
    except NotFoundError:
        return response_manager.error_404()
    except Exception:
        return response_manager.error_500()


@tests_bp.route('/check_answers', methods=['POST'])
@login_required()
def test_check_answers():
    try:
        data = request.get_json()
        if not data or 'test_id' not in data or 'user_answers' not in data:
            raise ValidationError()
        test = Test(test_id=data['test_id'])
        user = User(access_token=request.cookies.get('access_token'))
        result = test.check_answers(data['user_answers'], user.name)
        return response_manager.success_200(
            message=None,
            data=result
        )
    except ValidationError:
        return response_manager.error_400()
    except NotFoundError:
        return response_manager.error_404()
    except Exception:
        return response_manager.error_500()


@tests_bp.route('/delete', methods=['POST'])
@login_required()
def test_delete():
    try:
        data = request.get_json()
        if not data or 'test_id' not in data:
            raise ValidationError()
        test = Test(test_id=data['test_id'])
        test.delete_test()
        return response_manager.success_200(
            message={
                "ru-RU": "Тест успешно удалён",
                "en-US": "Test successfully deleted"
            }
        )
    except ValidationError:
        return response_manager.error_400()
    except NotFoundError:
        return response_manager.error_404()
    except (ConflictError, DatabaseError):
        return response_manager.error_500()
    except Exception:
        return response_manager.error_500()


@tests_bp.route('/archive', methods=['POST'])
@login_required()
def test_archive():
    try:
        data = request.get_json()
        if not data or 'test_id' not in data:
            raise ValidationError()
        test = Test(test_id=data['test_id'])
        test.archive_test()
        return response_manager.success_200(
            message={
                "ru-RU": "Тест архивирован",
                "en-US": "Test archived"
            }
        )
    except ValidationError:
        return response_manager.error_400()
    except NotFoundError:
        return response_manager.error_404()
    except Exception:
        return response_manager.error_500()


@tests_bp.route('/dearchive', methods=['POST'])
@login_required()
def test_dearchive():
    try:
        data = request.get_json()
        if not data or 'test_id' not in data:
            raise ValidationError()
        test = Test(test_id=data['test_id'])
        test.dearchive_test()
        return response_manager.success_200(
            message={
                "ru-RU": "Тест разархивирован",
                "en-US": "Test dearchived"
            }
        )
    except ValidationError:
        return response_manager.error_400()
    except NotFoundError:
        return response_manager.error_404()
    except Exception:
        return response_manager.error_500()