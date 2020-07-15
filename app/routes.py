import datetime
from app import app, bcrypt
from app.models import db, User, Todo
from flask import jsonify, request, url_for, redirect, jsonify, make_response
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import gen_salt
from authlib.integrations.flask_oauth2 import current_token
from .models import User, OAuth2Client
from .oauth2 import authorization, require_oauth
from .schemas import client_schema
from marshmallow import ValidationError

@app.route("/")
def home():
    return jsonify({"Info":"Hello world!"})

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data["username"]
    password = data["password"]
    remember = data["remember"]

    user = User.query.filter_by(username=username).first()
    if (user and user.check_password(password)):
        login_user(user, remember = remember)
        return jsonify({"Info":"Login Success!"})
    else:
        return jsonify({"Error":"Login Failed!"}), 403

@app.route("/logout", methods=["GET"])
def logout():
    logout_user()
    return jsonify({"Info":"Logged out!"})

@app.route("/create_client", methods=["GET", "POST"])
@login_required
def create_client():
    try:
        client_metadata = client_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 400

    client_id = gen_salt(24)
    client_id_isssued_at = int(datetime.datetime.now().timestamp())
    client = OAuth2Client(
        client_id=client_id,
        client_id_issued_at=client_id_isssued_at,
        user_id=current_user.id
    )
    
    client.set_client_metadata(client_metadata)

    if (client_metadata['token_endpoint_auth_method'] is None):
        client.client_secret = ''
    else:
        client.client_secret = gen_salt(48)
    
    db.session.add(client)
    db.session.commit()

    return jsonify({
        "Client Info": client.client_info,
        "Client Metadata": client.client_metadata
    })

    # client_id: NCQSMZYbcp9BvTr8bzQHgShJ
    # client_secret: Z6FOCqGKccyMctcaJv6NMDBFLNuTJuhKM5pK1YYfOoOjYpNH

@app.route("/oauth/token", methods=["POST"])
def issue_token():
    return authorization.create_token_response()

    # Token for AlpacaMax: uwFxtOUc1zLWaRch8rT60gDhHqphHSRU557FbHwbOP

@app.route('/oauth/revoke', methods=['POST'])
def revoke_token():
    return authorization.create_endpoint_response('revocation')