import os
import logging
import re

from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_oidc import OpenIDConnect
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix

from models import Base, UploadFile
from search_ask.custom_data_reader import slice_to_pages
from search_ask.weaviate_client import feed_vector_database, is_class_exists, create_class
from search_ask.find_answer import search_for_answer


load_dotenv()

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

app.config.update({
    'SECRET_KEY': os.environ['FLASK_SECRET_KEY'],
    'TESTING': True,
    'DEBUG': True,
    'OIDC_CLIENT_SECRETS': 'oidc-config.json',
    'OIDC_ID_TOKEN_COOKIE_SECURE': False,
    'OIDC_USER_INFO_ENABLED': True,
    'OIDC_OPENID_REALM': os.environ['FLASK_OIDC_OPENID_REALM'],
})
app.config["OIDC_SCOPES"] = ["openid", "email", "profile"]

oidc = OpenIDConnect(app)
os.makedirs(os.path.join(app.instance_path, 'upload_files'), exist_ok=True)

documentdb_user = os.environ['DOCUMENTDB_USER']
documentdb_password = os.environ['DOCUMENTDB_PASSWORD']
documentdb_host = os.environ['DOCUMENTDB_HOST']
documentdb_port = os.environ['DOCUMENTDB_PORT']
documentdb_database = os.environ['DOCUMENTDB_DATABASE']
documentdb_url = \
    (f'postgresql://'
     f'{documentdb_user}:{documentdb_password}@{documentdb_host}:{documentdb_port}/{documentdb_database}')
logging.debug(documentdb_url)
engine = create_engine(documentdb_url, echo=True)
Base.metadata.create_all(engine)


@app.route('/')
def home():
    # noinspection PyUnresolvedReferences
    return render_template('home.html')


@app.route('/chat', methods=['GET'])
@oidc.require_login
def chat_get():
    # noinspection PyDeprecation
    user_id = oidc.user_getinfo(['sub']).get('sub')

    with Session(engine) as session:
        stmt = select(UploadFile).where(UploadFile.user_id == user_id).distinct(UploadFile.category)
        upload_files = session.execute(stmt)
        categories = []
        for upload_file in upload_files:
            categories.append(upload_file[0].category)

        # noinspection PyUnresolvedReferences
        return render_template('chat.html', categories=categories)


@app.route('/chat', methods=['POST'])
@oidc.require_login
def chat_post():
    user_question = request.form.get("user_question")
    logging.debug(f"question: {user_question}")
    category = request.form.get("category")
    logging.debug(f"category: {category}")

    if user_question:
        answer = search_for_answer(category, user_question)
    else:
        flash('Bitte stelle deine Frage.')
        return redirect(url_for('chat_post'))

    # noinspection PyUnresolvedReferences
    return render_template('chat.html', answer=answer)


@app.route('/documents')
@oidc.require_login
def documents():
    # noinspection PyDeprecation
    user_id = oidc.user_getinfo(['sub']).get('sub')
    upload_files_model = load_documents(user_id)
    # noinspection PyUnresolvedReferences
    return render_template('documents.html', upload_files=upload_files_model)


def load_documents(user_id):
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
    return upload_files_model


@app.route('/import')
@oidc.require_login
def data_import():
    flash('Bitte vor dem Hochladen alle Sonderzeichen in den Dateinamen beseitigen.')
    # noinspection PyUnresolvedReferences
    return render_template('import.html')


@app.route('/documents/<int:file_id>', methods=['GET', 'POST'])
@oidc.require_login
def index(file_id):
    logging.debug(f"file_id: {file_id}")
    pages = []
    with Session(engine) as session:
        # noinspection PyDeprecation
        user_id = oidc.user_getinfo(['sub']).get('sub')
        upload_files_model = load_documents(user_id)

        stmt = select(UploadFile).where(file_id == UploadFile.id)
        file = session.execute(stmt).first()
        if file[0].status == "hochgeladen":
            filename = os.path.join(app.instance_path, 'upload_files', file[0].filename)
            pages = slice_to_pages(filename)

            if not is_class_exists(file[0].category):
                create_class(file[0].category)
            feed_vector_database(pages, file[0].category, file[0].user_id, file[0].id, filename, 10)

            file[0].status = "durchsuchbar"
            session.add(file[0])
            session.commit()

            upload_files_model = load_documents(user_id)

    # noinspection PyUnresolvedReferences
    return render_template('documents.html', upload_files=upload_files_model)


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
                # noinspection PyDeprecation
                user_id = oidc.user_getinfo(['sub']).get('sub')

                category = request.form.get('category')
                category = re.sub("[^A-Za-z0-9]+", "_", category).capitalize()

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
    # noinspection PyDeprecation
    user_info = oidc.user_getinfo(['sub', 'name', 'email'])
    # noinspection PyUnresolvedReferences
    return render_template('profile.html',
                           id=user_info.get('sub'),
                           name=user_info.get('name'),
                           email=user_info.get('email'))


@app.route('/logout')
def logout():
    logging.debug("Logging out...")
    oidc.logout()


if __name__ == '__main__':
    app.run()
