from service.db_init import db

class UserModel(db.Model):
    __tablename__ = "Users"
    id = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(50))
    groups_admin_of = db.Column(db.JSON)
    groups_user_of = db.Column(db.JSON)
    email = db.Column(db.String(50))
    avatar_url = db.Column(db.String(50))
    provider = db.Column(db.String(50))
    access_token = db.Column(db.Text)
    refresh_token = db.Column(db.Text)
    device_id = db.Column(db.String(256), nullable=True)
    token_expiry = db.Column(db.DateTime, nullable=True)
    

class TestModel(db.Model):
    __tablename__ = "Tests"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_ids = db.Column(db.String(500))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    is_visible = db.Column(db.Boolean, default=False)
    questions = db.Column(db.JSON)
    answers = db.Column(db.JSON)
    users_max_score = db.Column(db.Integer)
    users_attempts = db.Column(db.JSON)
    

class UserGroupModel(db.Model):
    __tablename__ = "UserGroups"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200))
    size = db.Column(db.Integer)
    admins = db.Column(db.JSON)
    users = db.Column(db.JSON)
    tests = db.Column(db.JSON)
    users_limit = db.Column(db.Integer)
    admins_limit = db.Column(db.Integer)

