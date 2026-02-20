import requests
from service.config import settings
from models import UserModel
from service.db_init import db

def update_access_token(access_token: str, refresh_token: str):
    try:
        data = {
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        response = requests.post(
            url="https://oauth2.googleapis.com/token",
            data=data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        response.raise_for_status()
        new_token = response.json()['access_token']
        user = UserModel.query.filter_by(access_token=access_token).first()
        if user:
            user.access_token = new_token
            db.session.commit()
            return new_token
        else:
            print("Пользователь с таким токеном не найден")
            return None
    except Exception as e:
        print(f'Не удалось обновить access token. Ошибка: \n {str(e)}')
