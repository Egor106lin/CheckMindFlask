import requests
from service.config import config
from models import UserModel
from service.db_init import db
from datetime import datetime, timedelta

class AccessTokenUpdater():
    def update_google_access_token(self, access_token: str, refresh_token: str):
        try:
            data = {
                'client_id': config.GOOGLE_CLIENT_ID,
                'client_secret': config.GOOGLE_CLIENT_SECRET,
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token'
            }
            response = requests.post(
                url="https://oauth2.googleapis.com/token",
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            response.raise_for_status()
            token_data = response.json()
            new_token = token_data['access_token']
            expires_in = token_data.get('expires_in')

            user = UserModel.query.filter_by(access_token=access_token).first()
            if user:
                user.access_token = new_token
                if expires_in:
                    user.token_expiry = datetime.now() + timedelta(seconds=expires_in)
                db.session.commit()
                return new_token
            else:
                return None
        except Exception as e:
            print(f'Не удалось обновить access token. Ошибка: \n {str(e)}')
            return None
        
    def update_vk_access_token(self, access_token: str, refresh_token: str):
        try:
            user = UserModel.query.filter_by(access_token=access_token).first()
            if not user:
                return None
            data = {
                'client_id': config.VK_CLIENT_ID,
                'client_secret': config.VK_CLIENT_SECRET,
                'refresh_token': refresh_token,
                'device_id': user.device_id,
                'grant_type': 'refresh_token'
            }
            response = requests.post(
                url="https://id.vk.ru/oauth2/auth",
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            response.raise_for_status()
            token_data = response.json()
            new_token = token_data['access_token']
            new_refresh_token = token_data.get('refresh_token')
            expires_in = token_data.get('expires_in')
            user.access_token = new_token
            if new_refresh_token:
                user.refresh_token = new_refresh_token
            if expires_in:
                user.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            db.session.commit()
            return new_token
        except Exception as e:
            print(f'Не удалось обновить VK access token. Ошибка: {str(e)}')
            return None
        
        
accessTokenUpdater = AccessTokenUpdater()
