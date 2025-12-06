from pydantic_core import Url
import requests
from service.config import settings
from models import UserModel
from service.db_init import db
import json

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
            headers={'content_type': 'application/x-www-form-urlencoded'}
        )
        user = UserModel.query.filter_by(access_token=access_token)
        user.access_token = json.loads(response.text)['access_token']
        db.session.commit()
    except Exception as e:
        print(f'Не удалось обновить access token. Ошибка: \n {str(e)}')
