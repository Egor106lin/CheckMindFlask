import requests
from functools import wraps

from flask import Flask, request, jsonify, Response, abort
from aiohttp import ClientSession

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from models import UserModel, TestModel, UserGroupModel

from service.db_init import db
from service.generate_links import generate_google_url
from service.config import settings
from service.jwt_decoder import jwt_decode
from service.create_user import create_user
#from flask_cors import CORS

import json

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)
with app.app_context():
    db.create_all()


def login_required(access_token=None):
    def decorator(function):
        @wraps(function)
        def decorated_function(*args, **kwargs):
            try:
                user = UserModel.query.filter_by(access_token=access_token).all()[0]
                if user:
                    pass
                else:
                    # переписать access токен на свежий
                    pass
            except Exception as e:
                return abort(401)
            return function(*args, **kwargs)
        return decorated_function
    return decorator


@app.route('/url/google', methods=['GET'])
def get_url_google():
    url = jsonify(generate_google_url())
    return url


@app.route('/auth/google', methods=['GET'])
async def auth_google():
    data = {
        'client_id': settings.GOOGLE_CLIENT_ID,
        'client_secret': settings.GOOGLE_CLIENT_SECRET,
        'code': request.values['code'],
        'grant_type': 'authorization_code',
        'redirect_uri': 'http://localhost:5000/auth/google'
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
    return '1'


@app.route('/tests/created_test', methods=['POST'])
def test_created_test():
    try:
        data = request.get_json()
        print({type(data)})
        print(json.dumps(data, indent=2, ensure_ascii=False))
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


@app.route('/tests/questions_and_options', methods=['GET'])
def test_questions_and_options():
    try:
        return jsonify({
            "status": "success", 
            "message": "Данные успешно отправлены",
            "data": '{"groupID": "123456789","questionsQuantity": 5,"testName": "Тест для отладки","testDescription": "Тест для проверки работы сайта","questionsAndOptions": [{"question": "1","options": [{"title": "1","correct": true},{"title": "2","correct": false}]},{"question": "2","options": [{"title": "1","correct": true},{"title": "2","correct": false},{"title": "3","correct": true},{"title": "4","correct": false}]},{"question": "3","options": [{"title": "1","correct": true},{"title": "3","correct": false},{"title": "4","correct": false},{"title": "6","correct": false},{"title": "2","correct": true},{"title": "70","correct": false},{"title": "ответ","correct": false}]},{"question": "4","options": [{"title": "ответ 1","correct": true},{"title": "ответ 2","correct": true}]},{"question": "5","options": [{"title": "1","correct": false},{"title": "2","correct": true}]}]}'
        }), 200
        
    except Exception as e:
        print(f"Ошибка при обработке запроса: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    

@app.route('/tests/check_answers', methods=['POST'])
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
    

@app.route('/groups/get_list', methods=['GET'])
@login_required(access_token='a')
def groups_get_list():
    try:
        users = UserModel.query.all()
        for user in users:
            print(f"\nID: {user.id}")
            print(f"Имя: {user.name}")
            print(f"Email: {user.email}")
            print(f"Провайдер: {user.provider}")
            print(f"Группы: {user.groups}")
            print(f"Аватар: {user.avatar_url}")
            print(f"Access token: {user.access_token}")
            print(f"Token expiry: {user.token_expiry}")
            print(f"Refresh token: {user.refresh_token}")
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
    

@app.route('/profile/user_data', methods=['GET'])
def profile_user_data():
    pass



if __name__ == '__main__':
    app.run(debug=True)
