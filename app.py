import os
import logging

from dotenv import load_dotenv
from flask import Flask, render_template, request
from flask_oidc import OpenIDConnect
from werkzeug.utils import secure_filename

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

os.makedirs(os.path.join(app.instance_path, 'upload_files'), exist_ok=True)

oidc = OpenIDConnect(app)


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
    info = oidc.user_getinfo(['email', 'openid_id'])
    return ('Hello, %s (%s)! <a href="/">Return</a>' %
            (info.get('email'), info.get('openid_id')))


@app.route('/data_import')
@oidc.require_login
def data_import():
    email = oidc.user_getfield('email')
    return render_template('data_import.html', base_url=base_url)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        file.save(os.path.join(app.instance_path, 'upload_files', secure_filename(file.filename)))
        return 'File uploaded successfully'


@app.route('/logout')
def logout():
    oidc.logout()
    return 'Hi, you have been logged out! <a href="/">Return</a>'


if __name__ == '__main__':
    app.run()
