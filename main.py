import requests

from flask import Flask, request, jsonify, Response, abort, redirect
from aiohttp import ClientSession

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from models import UserModel, TestModel, UserGroupModel
from entities import User

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


@app.route('/api/tests/questions_and_options', methods=['GET'])
@login_required()
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


if __name__ == '__main__':
    app.run(debug=True)
