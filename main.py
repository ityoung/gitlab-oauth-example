from flask import Flask, redirect, url_for, session, jsonify
from authlib.flask.client import OAuth, RemoteApp
from loginpass import create_gitlab_backend, register_to

OAUTH_APP_NAME = 'gitlab'
GITLAB_HOST = 'YOUR_GITLAB_HOST'
GITLAB_CLIENT_ID = 'YOUR_APP_ID'
GITLAB_CLIENT_SECRET = 'YOUR_APP_SECRET_KEY'
SESSION_SECRET_KEY = 'YOUR_SECRET_KEY'

app = Flask(__name__)
# Copy these two configuration from GitLab > User Settings > Applications
app.config['GITLAB_CLIENT_ID'] = GITLAB_CLIENT_ID
app.config['GITLAB_CLIENT_SECRET'] = GITLAB_CLIENT_SECRET
# Set SECRET_KEY to encrypt cookies
app.config['SECRET_KEY'] = SESSION_SECRET_KEY


def fetch_token(name):
    token_session_key = '{}-token'.format(name.lower())
    return session.get(token_session_key, {})


def update_token(name, token):
    token_session_key = '{}-token'.format(name.lower())
    session[token_session_key] = token
    return token


# Create a registry
# Setting `fetch_token` and `update_token` to make token available for
# `oauth_token` in some other routes
oauth = OAuth(app, fetch_token=fetch_token, update_token=update_token)
# Setting gitlab backend, like urls
gitlab_backend = create_gitlab_backend(OAUTH_APP_NAME, GITLAB_HOST)
# Register an oauth_client
oauth_client = register_to(gitlab_backend, oauth, RemoteApp)


@app.route('/login')
def login():
    """
    Login Api, sometimes triggered when clicking login button.
    """
    redirect_uri = url_for('auth', _external=True)
    return oauth_client.authorize_redirect(redirect_uri)


@app.route('/auth')
def auth():
    """
    Auth Api, called by login.
    """
    token = oauth_client.authorize_access_token()
    # save token inside session
    update_token(OAUTH_APP_NAME, token)
    return redirect(url_for('profile', _external=True))


@app.route('/profile')
def profile():
    """
    Show profiles, called after logged in.
    """
    # get token manually to RemoteApp
    token = fetch_token(OAUTH_APP_NAME)
    return jsonify(oauth_client.profile())


app.run('127.0.0.1', '5000', debug=True)
