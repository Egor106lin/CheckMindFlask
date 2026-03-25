from flask import Blueprint, g, request, jsonify
from service.login_required import login_required
from entities import User, Test, Group

tests_bp = Blueprint('tests', __name__)

@tests_bp.route('/created_test', methods=['POST'])
@login_required()
def test_created_test():
    try:
        data = request.get_json()
        new_test = Test()
        new_test.create_new(data)
        user = User()
        user.create_with_token(request.cookies.get('access_token'))
        group_with_this_test = Group()
        group_with_this_test.create_with_id(data['groupID'])
        if group_with_this_test.is_admin(user.id):
            group_with_this_test.add_test(new_test.id)
            return jsonify({
                "status": "success", 
                "message": "Данные успешно получены",
                "received_data": data
            }), 200
        else:
            return jsonify({
                "status": "error",
            }), 403
        
    except Exception as e:
        print(f"Ошибка при обработке запроса: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


@tests_bp.route('/questions_and_options', methods=['POST'])
@login_required()
def test_questions_and_options():
    try:
        request_data = request.get_json()['params']
        test_id = request_data['test_id']
        user = g.user
        test_to_send = Test()
        test_to_send.create_with_id(test_id)
        group_with_test = Group()
        if group_with_test.create_with_id(test_to_send.groups[0]):
            if group_with_test.is_user(user.id) and test_to_send.is_visible:
                return jsonify({
                    "status": "success", 
                    "data": test_to_send.to_frontend_format()
                }), 200
            else:
                return jsonify({
                    "status": "error",
                }), 403
        
    except Exception as e:
        print(f"Ошибка при обработке запроса: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    

@tests_bp.route('/get_groups_to_create_test', methods=['GET'])
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



@tests_bp.route('/check_answers', methods=['POST'])
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
    

@tests_bp.route('/delete', methods=['POST'])
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
    

@tests_bp.route('/archive', methods=['POST'])
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
    

@tests_bp.route('/dearchive', methods=['POST'])
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