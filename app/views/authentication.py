from hashlib import new
from flask import jsonify, request
from werkzeug.exceptions import abort
from passlib.hash import sha256_crypt
from flask_jwt_extended import (
    create_access_token,
     get_jwt_identity,
    jwt_required
)
from app import bp, db
from app.models import User
from datetime import datetime
from core.utils import validate_request_schema, generate_4_digit

ALLOWED_ROLES = ['admin', 'superadmin']


@bp.route('/login', methods=['POST'])
def authenticate_user():
    schema = {
        'username': {'type': 'string', 'required': True, 'empty': False},
        'password': {'type': 'string', 'required': True, 'empty': False}
    }
    validate_request_schema(schema, request.json)

    user = User.query.filter_by(username=request.json['username']).\
        first_or_404(description="Invalid username & password combination")

    username = user.username
    role = user.role

    # get the hashed password from the db based on the supplied username
    db_password = user.password

    # validate user password
    if not sha256_crypt.verify(request.json['password'], db_password):
        abort(401, "Invalid username & password combination")

    if user.status != "Active":
        abort(401, "User account has been disabled")
    if user.branch_uuid == None:
        branch = "master"
    else:
        branch = user.branch.name
    identity = username + ':' + role + ':' + branch
    
    tokens = {
        'access_token': create_access_token(identity=identity),
        'refresh_token': 'create_refresh_token(identity=identity)',
        'username': username
        }
    return jsonify(
        {
            'status': 200,
            'message': "Authenticated",
            'role': role,
            'branch': branch,
            "tokens": tokens
        }), 200


@bp.route('/refresh', methods=['GET'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    token = {
        'access_token': create_access_token(identity=identity),
        'username': identity.split(':')[0]
    }
    return jsonify(token), 200


@bp.route('/user/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    schema = {
        'old_password': {'type': 'string', 'required': True, 'empty': False},
        'new_password': {'type': 'string', 'required': True, 'empty': False},
        'password_confirmation': {'type': 'string', 'required': True, 'empty': False}
    }
    validate_request_schema(schema, request.json)

    doctor = User.query.filter_by(username=get_jwt_identity().split(":")[0]).\
        first_or_404(description='invalid username supplied')
    db_password = doctor.password

    # validate current password
    if not sha256_crypt.verify(request.json['old_password'], db_password):
        abort(400, "Supplied current password is invalid")

    # validate that new password and password confirmation match
    if request.json['new_password'] != request.json['password_confirmation']:
        abort(400, "New passwords do not match")

    # hash the new password
    request.json['new_password'] = sha256_crypt.encrypt(str(request.json.get('new_password')))
    doctor.password = request.json['new_password']
    doctor.form_author = get_jwt_identity().split(":")[0]
    doctor.form_date = datetime.utcfromtimestamp(datetime.now().timestamp() + 7200). \
        strftime('%Y-%m-%d %H:%M:%S')

    db.session.commit()
    return jsonify({"message": "Password updated successfully"})


@bp.route('/reset-password', methods=['PUT'])
@jwt_required()
def reset_password():
    if get_jwt_identity().split(":")[1] not in ALLOWED_ROLES:
        abort(401, "Unauthorized to access this resource")
    username = request.args.get('username')
    if not username:
        return jsonify({"error": "username param is missing"}), 400

    doctor = User.query.filter_by(username=username).\
        first_or_404(description='invalid username supplied')

    doctor.password = sha256_crypt.encrypt('neccube@2023')
    doctor.updated = datetime.utcfromtimestamp(datetime.now().timestamp() + 7200). \
        strftime('%Y-%m-%d %H:%M:%S')
    doctor.action_author = get_jwt_identity().split(":")[0]

    db.session.commit()
    return jsonify({"message": "Password reset successfully"})


@bp.route('/deactivate', methods=['PUT'])
@jwt_required()
def deactivate_user():
    if get_jwt_identity().split(":")[1] not in ALLOWED_ROLES:
        abort(401, "Unauthorized to access this resource")

    uuid = request.args.get('uuid')
    if not uuid:
        abort(400, "uuid param is missing")

    user = User.query.filter_by(uuid=uuid).\
        first_or_404(description='invalid uuid supplied')

    user.status = "Inactive"
    user.action_author = get_jwt_identity().split(":")[0]
    user.updated = datetime.utcfromtimestamp(datetime.now().timestamp() + 7200). \
        strftime('%Y-%m-%d %H:%M:%S')
    db.session.commit()
    return jsonify({"message": "user deactivated successfully"})


@bp.route('/activate', methods=['PUT'])
@jwt_required()
def activate_user():
    if get_jwt_identity().split(":")[1] not in ALLOWED_ROLES:
        abort(401, "Unauthorized to access this resource")

    uuid = request.args.get('uuid')
    if not uuid:
        abort(400, "Username param is missing")

    user = User.query.filter_by(uuid=uuid).\
        first_or_404(description='invalid uuid supplied')

    user.status = "Active"
    user.action_author = get_jwt_identity().split(":")[0]
    user.updated = datetime.utcfromtimestamp(datetime.now().timestamp() + 7200). \
        strftime('%Y-%m-%d %H:%M:%S')
    db.session.commit()
    return jsonify({"message": "User activated successfully"})
