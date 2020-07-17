import datetime
from app import app, bcrypt
from app.models import db, User, Todo
from flask import jsonify, request, url_for, redirect, jsonify, make_response
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import gen_salt
from authlib.integrations.flask_oauth2 import current_token
from .models import User, OAuth2Client
from .oauth2 import authorization, require_oauth
from .schemas import client_schema, user_register_schema, user_schema, todo_schema
from marshmallow import ValidationError

@app.route("/coffee", methods=["POST"])
def brew_coffee_in_teapot():
    return jsonify({"error":"I'm a teapot!"}), 418

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

@app.route("/client", methods=["POST"])
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
    }), 201

    # AlpacaMax
    # client_id: NCQSMZYbcp9BvTr8bzQHgShJ
    # client_secret: Z6FOCqGKccyMctcaJv6NMDBFLNuTJuhKM5pK1YYfOoOjYpNH

    # Gilbert
    # client_id: D08Nqtgmyf9Ki4o02lECii4W
    # client_secret: bFwERKDQ4OIjR2TM0EDd8obRH6Gh4fCRG8hx8BgSVSdwPts4

@app.route("/oauth/token", methods=["POST"])
def issue_token():
    return authorization.create_token_response()

    # Token for AlpacaMax: uwFxtOUc1zLWaRch8rT60gDhHqphHSRU557FbHwbOP
    # Token for Gilbert: 40ACoq15Wt5iA2MndxPGul30KIvuwx0F30qKAnXtqx

@app.route('/oauth/revoke', methods=['POST'])
def revoke_token():
    return authorization.create_endpoint_response('revocation')

# Register a user
@app.route('/user', methods=['POST'])
def register_user():
    try:
        data = user_register_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    user = User(
        username = data["username"],
        password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "Info": "User created!"
    }), 201

# Delete a user
@app.route('/user/<int:user_id>', methods=["DELETE"])
@require_oauth('profile')
def delete_user(user_id):
    token_user = current_token.user
    target_user = User.query.get(user_id)

    if (target_user is None):
        return jsonify({"error":"User not found!"}), 404
    elif (token_user is target_user):
        if (current_user is target_user):
            logout()

        db.session.delete(target_user)
        db.session.commit()
        return jsonify({"info":"User deleted!"})
    else:
        return jsonify({"error":"Unauthorized user!"}), 401

# Get user info
@app.route("/user/<int:user_id>", methods=["GET"])
@require_oauth('profile')
def view_user(user_id):
    token_user = current_token.user
    target_user = User.query.get(user_id)

    if (target_user is None):
        return jsonify({"error":"User not found!"}), 404
    elif (token_user is target_user):
        result = user_schema.dump(target_user)
        return jsonify(result)
    else:
        return jsonify({"error":"Unauthorized user!"}), 401

# Update user info
@app.route("/user/<int:user_id>", methods=["PUT"])
@require_oauth('profile')
def update_user(user_id):
    token_user = current_token.user
    target_user = User.query.get(user_id)

    if (target_user is None):
        return jsonify({"error":"User not found!"}), 404
    elif (token_user is target_user):
        data = request.get_json()

        if ("username" in data):
            target_user.username = data["username"]
        if ("password" in data):
            target_user.password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
        
        db.session.add(target_user)
        db.session.commit()

        return jsonify({"info":"User info updated"})
    else:
        return jsonify({"error":"Unauthorized user!"}), 401

# Create a Todo
@app.route("/todo", methods=["POST"])
@require_oauth('profile')
def create_todo():
    try:
        data = todo_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 400

    user = current_token.user

    todo = Todo(
        user_id = user.id,
        name = data["name"],
        year = data["year"],
        month = data["month"],
        week = data["week"],
        day = data["day"]
    )
    db.session.add(todo)
    db.session.commit()

    return jsonify({"info":"Todo created!"}), 201