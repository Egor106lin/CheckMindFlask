from models import UserModel
from service.db_init import db

def create_user(data: dict, provider: str):
    try:
        user_id = str(data.get('sub'))
        user_with_same_id = UserModel.query.get(user_id)
        user = UserModel(
            id=user_id,
            name=data.get('name'),
            email=data['email'],
            avatar_url=data.get('picture'),
            provider=provider,
            groups=[],
            access_token=data.get('access_token'),
            refresh_token=data.get('refresh_token'),
            token_expiry=data.get('token_expiry')
        )
        if user_with_same_id != None:
            user_with_same_id.name = data.get('name')
            user_with_same_id.email = data['email']
            user_with_same_id.avatar_url = data.get('picture')
            user_with_same_id.provider = provider
            user_with_same_id.access_token = data.get('access_token')
            user_with_same_id.refresh_token = data.get('refresh_token')
            user_with_same_id.token_expiry = data.get('token_expiry')
        else:
            db.session.add(user)
        db.session.commit()
    except Exception as e:
        print(e)