from models import UserModel


class User():
    def __init__(self, user_id=None):
        if user_id:
            self.create_with_id(user_id)
    
    def create_with_id(self, user_id):
        user_data = UserModel.query.get(user_id)
        if user_data:
            self.id = user_data.id
            self.name = user_data.name
            self.groups = user_data.groups
            self.email = user_data.email
            self.avatar_url = user_data.avatar_url
            self.provider = user_data.provider
            self.access_token = user_data.access_token
            self.refresh_token = user_data.refresh_token
            self.token_expiry = user_data.token_expiry
    
    def create_with_token(self, access_token):
        if not access_token:
            return None
        
        user_data = UserModel.query.filter_by(access_token=access_token).first()
        
        if user_data:
            self.id = user_data.id
            self.name = user_data.name
            self.groups = user_data.groups
            self.email = user_data.email
            self.avatar_url = user_data.avatar_url
            self.provider = user_data.provider
            self.access_token = user_data.access_token
            self.refresh_token = user_data.refresh_token
            self.token_expiry = user_data.token_expiry
