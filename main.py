from flask import Flask
from flask_migrate import Migrate

from service.db_init import db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)
with app.app_context():
    db.create_all()

from blueprints.auth import auth_bp
from blueprints.groups import groups_bp
from blueprints.tests import tests_bp
from blueprints.invites import invites_bp
from blueprints.profile import profile_bp

app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(groups_bp, url_prefix='/api/groups')
app.register_blueprint(tests_bp, url_prefix='/api/tests')
app.register_blueprint(invites_bp, url_prefix='/api/invite')
app.register_blueprint(profile_bp, url_prefix='/api/profile')

if __name__ == '__main__':
    app.run(debug=True)
