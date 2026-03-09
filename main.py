from flask import Flask
from flask_migrate import Migrate

from service.db_init import db
from service.config import config

from blueprints.auth import auth_bp
from blueprints.groups import groups_bp
from blueprints.tests import tests_bp
from blueprints.invites import invites_bp
from blueprints.profile import profile_bp

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)
if config.FLASK_DEBUG:
    with app.app_context():
        db.create_all()

app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(groups_bp, url_prefix='/api/groups')
app.register_blueprint(tests_bp, url_prefix='/api/tests')
app.register_blueprint(invites_bp, url_prefix='/api/invite')
app.register_blueprint(profile_bp, url_prefix='/api/profile')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
