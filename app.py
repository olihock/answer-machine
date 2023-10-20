import os
import logging

from dotenv import load_dotenv
from flask import Flask, render_template, request
from flask_oidc import OpenIDConnect
from sqlalchemy.orm import Session
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine

from models import Base, UploadFile

load_dotenv()
base_url = os.environ['APP_BASE_URL']

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config.update({
    'SECRET_KEY': os.environ['FLASK_SECRET_KEY'],
    'TESTING': True,
    'DEBUG': True,
    'OIDC_CLIENT_SECRETS': 'openid-config.json',
    'OIDC_ID_TOKEN_COOKIE_SECURE': False,
    'OIDC_USER_INFO_ENABLED': True,
    'OIDC_OPENID_REALM': os.environ['FLASK_OIDC_OPENID_REALM'],
})

oidc = OpenIDConnect(app)

os.makedirs(os.path.join(app.instance_path, 'upload_files'), exist_ok=True)

filedb_user = os.environ['SQLALCHEMY_FILEDB_USER']
filedb_password = os.environ['SQLALCHEMY_FILEDB_PASSWORD']
filedb_host = os.environ['SQLALCHEMY_FILEDB_HOST']
filedb_port = os.environ['SQLALCHEMY_FILEDB_PORT']
filedb_database = os.environ['SQLALCHEMY_FILEDB_DATABASE']
filedb_url = f'postgresql+psycopg2://{filedb_user}:{filedb_password}@{filedb_host}:{filedb_port}/{filedb_database}'
logging.debug(filedb_url)
engine = create_engine(filedb_url, echo=True)
Base.metadata.create_all(engine)


@app.route('/')
def home():
    if oidc.user_loggedin:
        return ('Hi %s, <a href="/profile">See profile</a> '
                '<a href="/logout">Log out</a>') % \
            oidc.user_getfield('email')
    else:
        return 'Welcome anonymous, <a href="/profile">Log in</a>'


@app.route('/profile')
@oidc.require_login
def profile():
    user_info = oidc.user_getinfo(['sub', 'name', 'email'])
    return render_template('user_profile.html',
                           id=user_info.get('sub'),
                           name=user_info.get('name'),
                           email=user_info.get('email'))


@app.route('/data_import')
@oidc.require_login
def data_import():
    user_info = oidc.user_getinfo(['email', 'openid_id'])
    return render_template('data_import.html', base_url=base_url)


@app.route('/upload', methods=['GET', 'POST'])
@oidc.require_login
def upload():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.instance_path, 'upload_files', filename))

        with Session(engine) as session:
            # sub is the uuid from keycloak
            user_id = oidc.user_getinfo(['sub']).get('sub')
            category = request.form.get('category')
            upload_file = UploadFile(user_id=user_id, category=category, filename=filename)
            session.add(upload_file)
            session.commit()

        return 'File uploaded successfully'


@app.route('/logout')
def logout():
    oidc.logout()
    return 'Hi, you have been logged out! <a href="/">Return</a>'


if __name__ == '__main__':
    app.run()
