from datetime import datetime, timedelta
from flask import current_app

from models import UserModel
from service.db_init import db

def create_user(data: dict, provider: str):
    try:
        user_id = str(data.get('sub'))
        user = UserModel.query.get(user_id)
        expires_in = data.get('token_expiry')
        token_expiry = None
        if expires_in:
            token_expiry = datetime.now() + timedelta(seconds=expires_in)
        if user:
            user.name = data.get('name')
            user.email = data['email']
            user.avatar_url = data.get('picture')
            user.provider = provider
            user.access_token = data.get('access_token')
            user.refresh_token = data.get('refresh_token')
            user.token_expiry = token_expiry
        else:
            user = UserModel(
                id=user_id,
                name=data.get('name'),
                email=data['email'],
                avatar_url=data.get('picture'),
                provider=provider,
                groups_admin_of=[],
                groups_user_of=[],
                access_token=data.get('access_token'),
                refresh_token=data.get('refresh_token'),
                token_expiry=token_expiry
            )
            db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Failed to create/update user: {e}", exc_info=True)