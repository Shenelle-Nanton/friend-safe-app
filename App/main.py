import os
from flask import Flask
from flask_login import LoginManager, current_user
from flask_uploads import DOCUMENTS, IMAGES, TEXT, UploadSet, configure_uploads
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from datetime import timedelta

from App.database import init_db
from App.config import config

from App.controllers import (
    setup_jwt,
    setup_flask_login
)

from App.views import views

def add_views(app):
    for view in views:
        app.register_blueprint(view)

def configure_app(app, config, overrides):
    for key, value in config.items():
        if key in overrides:
            app.config[key] = overrides[key]
        else:
            app.config[key] = config[key]

def create_app(config_overrides={}):
    app = Flask(__name__, static_url_path='/static')
    configure_app(app, config, config_overrides)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEVER_NAME'] = '0.0.0.0'
    app.config['PREFERRED_URL_SCHEME'] = 'https'
    app.config['UPLOADED_PHOTOS_DEST'] = "App/uploads"
    CORS(app)
    photos = UploadSet('photos', TEXT + DOCUMENTS + IMAGES)
    configure_uploads(app, photos)
    add_views(app)
    init_db(app)
    setup_jwt(app)
    setup_flask_login(app)
    app.app_context().push()
    return app

@app.route('/', methods=['GET'])
@app.route('login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/signup',methods=['GET'])
def signup_page():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_action():
    data = request.form
    newuser = RegularUser(username=data['username'], email=data['email'], password=data['password'])
    try:
        db.session.add(newuser)
        db.session.commit()
        login_user(newuser)
        flash('Account Created!')
        return redirect(url_for())
    except Exception:
        db.session.rollback()
        flash("Username or Email already exists!")
    return redirect(url_for('**'))

@app.route('/login', methods=['GET'])
def login_action():
    data = request.form
    user = RegularUser.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        flash('Logged In Successfully')
        login_user(user)
        return redirect('/**')

    admin = Admin.query.filter_by(username=data['username']).first()
    if admin and admin.check_password(data['password']):
        flash('Logged In Successfully')
        login_user(admin)
        return redirect('/**')

    flash('Invalid Username or Password')
    return redirect('/')

@app.route('logout', methods=['GET'])
def logout_action():
    logout_user()
    flash('Logged Out')
    return redirect(url_for('login_page'))

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=81)
