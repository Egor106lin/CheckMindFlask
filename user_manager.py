from models import UserModel


class User():
    def __init__(self, user_data=None, **kwargs):
        if user_data:
            self.create_from_db(user_data)
        else:
            self.create_from_kwargs(kwargs)
    
    def create_from_db(self, user_data):
        self.id = user_data.id
        self.name = user_data.name
        self.groups = user_data.groups
        self.email = user_data.email
        self.avatar_url = user_data.avatar_url
        self.provider = user_data.provider
        self.access_token = user_data.access_token
        self.refresh_token = user_data.refresh_token
        self.token_expiry = user_data.token_expiry

    def create_from_kwargs(self, kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.groups = kwargs.get('groups')
        self.email = kwargs.get('email')
        self.avatar_url = kwargs.get('avatar_url')
        self.provider = kwargs.get('provider')
        self.access_token = kwargs.get('access_token')
        self.refresh_token = kwargs.get('refresh_token')
        self.token_expiry = kwargs.get('token_expiry')
    
    def create_from_token(self, access_token):
        if not access_token:
            return None
        
        user_data = UserModel.query.filter_by(access_token=access_token).first()
        
        if user_data:
            return {
                "id": user_data.id,
                "name": user_data.name,
                "groups": user_data.groups,
                "email": user_data.email,
                "avatar_url": user_data.avatar_url,
                "provider": user_data.provider,
                "access_token": user_data.access_token,
                "refresh_token": user_data.refresh_token,
                "token_expiry": user_data.token_expiry
            }
