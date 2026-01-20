from service.db_init import db

class UserModel(db.Model):
    __tablename__ = "Users"
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(50))
    groups = db.Column(db.JSON)
    email = db.Column(db.String(50))
    avatar_url = db.Column(db.String(50))
    provider = db.Column(db.String(50))
    access_token = db.Column(db.Text)
    refresh_token = db.Column(db.Text)
    token_expiry = db.Column(db.Integer)
    

class TestModel(db.Model):
    __tablename__ = "Tests"
    id = db.Column(db.Integer, primary_key=True)
    group_ids = db.Column(db.String(500))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    is_visible = db.Column(db.Boolean, default=False)
    questions = db.Column(db.Text)
    correct_answers = db.Column(db.Text)
    users_max_score = db.Column(db.Integer)
    users_attempts = db.Column(db.Integer)
    

class UserGroupModel(db.Model):
    __tablename__ = "UserGroups"
    id = db.Column(db.Integer, primary_key=True)
    admins = db.Column(db.JSON)
    users = db.Column(db.JSON)
    tests = db.Column(db.JSON)

