import os
import logging

from dotenv import load_dotenv
from flask import Flask, render_template, request
from flask_oidc import OpenIDConnect
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select
from werkzeug.utils import secure_filename

from models import Base, UploadFile

load_dotenv()

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config.update({
    'SECRET_KEY': os.environ['FLASK_SECRET_KEY'],
    'TESTING': True,
    'DEBUG': True,
    'OIDC_CLIENT_SECRETS': {
        "web": {
            "issuer": os.environ['OIDC_ISSUER'],
            "client_id": os.environ['OIDC_CLIENT_ID'],
            "client_secret": os.environ['OIDC_CLIENT_SECRET']
        }
    },
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
    return render_template('home.html')


@app.route('/answer')
@oidc.require_login
def answer():
    return render_template('answer.html')


@app.route('/documents')
@oidc.require_login
def documents():
    user_id = oidc.user_getinfo(['sub']).get('sub')
    with Session(engine) as session:
        stmt = select(UploadFile).where(UploadFile.user_id == user_id)
        upload_files = session.execute(stmt)
        upload_files_model = []
        for upload_file in upload_files:
            upload_files_model.append({
                "id": upload_file[0].id,
                "category": upload_file[0].category,
                "filename": upload_file[0].filename,
                "status": upload_file[0].status
            })
    return render_template('documents.html', upload_files=upload_files_model)


@app.route('/import')
@oidc.require_login
def data_import():
    return render_template('import.html')


@app.route('/upload', methods=['GET', 'POST'])
@oidc.require_login
def upload():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.instance_path, 'upload_files', filename))

        with Session(engine) as session:
            stmt = select(UploadFile).where(UploadFile.filename == filename)
            upload_files = session.execute(stmt).all()
            if len(upload_files) == 0:
                # sub is the uuid from keycloak
                user_id = oidc.user_getinfo(['sub']).get('sub')
                category = request.form.get('category')
                status = "hochgeladen"
                upload_file = UploadFile(user_id=user_id, category=category, filename=filename, status=status)
                session.add(upload_file)
                session.commit()
                return 'File uploaded successfully.'
            else:
                return 'File already uploaded.'


@app.route('/profile')
@oidc.require_login
def profile():
    user_info = oidc.user_getinfo(['sub', 'name', 'email'])
    return render_template('profile.html',
                           id=user_info.get('sub'),
                           name=user_info.get('name'),
                           email=user_info.get('email'))


@app.route('/logout')
def logout():
    logging.debug("Logging out...")
    oidc.logout()


if __name__ == '__main__':
    app.run(host='0.0.0.0')
