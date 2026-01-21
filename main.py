import requests

from flask import Flask, request, jsonify, Response, abort, redirect
from aiohttp import ClientSession

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from models import UserModel, TestModel, UserGroupModel
from entities import User, Group, Test

from service.db_init import db
from service.generate_links import generate_google_url
from service.config import settings
from service.jwt_decoder import jwt_decode
from service.create_user import create_user
from service.update_access_token import update_access_token
from service.login_required import login_required

import json

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
        create_user(user_data, 'google')
        response = redirect(f'{settings.FRONTEND_URL}/profile')
        response.set_cookie('access_token', user_data['access_token'], httponly=True)
        return response
    except Exception as e:
        print(e)
        return abort(500)


@app.route('/api/tests/created_test', methods=['POST'])
@login_required()
def test_created_test():
    try:
        data = request.get_json()
        new_test = Test()
        new_test.create_new(data)
        tests = TestModel.query.all()

        # Вывести каждую запись
        for test in tests:
            print(f"ID: {test.id}")
            print(f"Title: {test.title}")
            print(f"Description: {test.description}")
            print(f"Group IDs: {test.group_ids}")
            print(f"Is Visible: {test.is_visible}")
            print(f"Questions: {test.questions}")
            print(f"Correct Answers: {test.correct_answers}")
            print(f"Users Max Score: {test.users_max_score}")
            print(f"Users Attempts: {test.users_attempts}")
            print("-" * 50)
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


@app.route('/api/tests/questions_and_options', methods=['GET'])
@login_required()
def test_questions_and_options():
    try:
        return jsonify({
            "status": "success", 
            "message": "Данные успешно отправлены",
            "data": '{"groupID":"123456789","questionsQuantity":5,"testName":"Тест для отладки","testDescription":"Тест для отладки основных функций на фронте","questionsAndOptions":[{"question":"1","options":[{"title":"ответ","correct":false},{"title":"ответ","correct":true},{"title":"вопрос","correct":false}]},{"question":"2","options":[{"title":"3","correct":false},{"title":"2","correct":true}]},{"question":"1","options":[{"title":"4","correct":true},{"title":"7","correct":false}]},{"question":"вопрос 4","options":[{"title":"ответ 1","correct":false},{"title":"ответ 2","correct":true},{"title":"ответ 3","correct":false}]},{"question":"вопрос 5","options":[{"title":"ответ 10","correct":false},{"title":"ответ 17","correct":false},{"title":"ответ 42","correct":false},{"title":"ответ 44","correct":false},{"title":"1","correct":false},{"title":"2","correct":false},{"title":"4","correct":true},{"title":"8","correct":false},{"title":"9","correct":false},{"title":"10","correct":false}]}]}'
        }), 200
        
    except Exception as e:
        print(f"Ошибка при обработке запроса: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    

@app.route('/api/tests/check_answers', methods=['POST'])
@login_required()
def test_check_answers():
    try:
        return jsonify({
            "status": "success", 
            "message": "Данные успешно получены",
            "data": '{"groupID":"123456789","questionsQuantity":5,"testName":"Тест для отладки","testDescription":"Описание теста для отладки. С помощью него можно сверстать страницу, на которой нужен готовый тест.","result":"4","mistakes":[{"question":"Вопрос 1","correct":true},{"question":"Вопрос 2","correct":true},{"question":"Вопрос 3","correct":false},{"question":"Вопрос 4","correct":true},{"question":"Вопрос 5","correct":false}]}'
        }), 200
        
    except Exception as e:
        print(f"Ошибка при обработке запроса: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    

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


@app.route('/api/groups/get_list', methods=['GET'])
@login_required()
def groups_get_list():
    try:
        return jsonify({
            "status": "success", 
            "message": "Данные успешно отправлены",
            "data": '[{"number":1,"owner":"Александр","group_size":15,"name":"Проект","ID":"123456789"},{"number":2,"owner":"Мария","group_size":8,"name":"Группа","ID":"987654321"},{"number":3,"owner":"Иван","group_size":22,"name":"Команда","ID":"456123789"},{"number":4,"owner":"Ольга","group_size":5,"name":"Отдел","ID":"321654987"},{"number":5,"owner":"Дмитрий","group_size":17,"name":"Разработка","ID":"789123456"}]'
        }), 200
        
    except Exception as e:
        print(f"Ошибка при обработке запроса: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    

@app.route('/api/groups/get_members', methods=['GET'])
@login_required()
def groups_get_members():
    try:
        print(request.args.get('params[groupID]'))
        return jsonify({
            "status": "success", 
            "message": "Данные успешно отправлены",
            "data": '[{"number":1,"name":"Том","admin":true},{"number":2,"name":"Том"},{"number":3,"name":"Том","admin":true},{"number":4,"name":"Том"}]'
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
    user = User()
    group = Group()
    user.create_with_token(request.cookies.get('access_token'))
    group.delete_user(user)
    user_id = request.get_json()
    return jsonify({
        "status": "success", 
        "message": "Группа удалена",
    }), 200


@app.route('/api/groups/leave', methods=['POST'])
@login_required()
def leave_group():
    user_id = request.get_json()
    print(request.data)
    return jsonify({
        "status": "success", 
        "message": "Группа покинута",
    }), 200


@app.route('/api/groups/create', methods=['POST'])
@login_required()
def create_group():
    try:
        group_title = request.get_json().get('group_title')
        if group_title:
            user = User()
            group_to_create = Group()
            user.create_with_token(request.cookies.get('access_token'))
            success = group_to_create.create_new(group_title)
        groups = UserGroupModel.query.all()

        for group in groups:
            print(f"ID: {group.id}")
            print(f"Title: {group.title}")
            print(f"Size: {group.size}")
            print(f"Admins: {group.admins}")
            print(f"Users: {group.users}")
            print(f"Tests: {group.tests}")
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
        return jsonify({
            "status": "error",
            "message": "Что-то пошло не так"
        }), 500


@app.route('/api/groups/join', methods=['POST'])
@login_required()
def join_group():
    user_id = request.get_json()
    print(request.data)
    return jsonify({
        "status": "success", 
        "message": "Вы присоединены к группе",
    }), 200


if __name__ == '__main__':
    app.run(debug=True)
