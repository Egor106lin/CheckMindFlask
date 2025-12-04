from models import UserModel
from service.db_init import db

def create_user(data: dict, provider: str):
    # TODO - check, do we have this user in our db
    user = UserModel(
        name=data.get('name'),
        email=data['email'],
        avatar_url=data.get('picture'),
        provider=provider,
        groups=[],
        access_token=None,
        refresh_token=None,
        token_expiry=None
    )
    db.session.add(user)
    db.session.commit()
    
