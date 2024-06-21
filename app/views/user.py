from hashlib import new
from flask import jsonify, request,Blueprint
from werkzeug.exceptions import abort
from passlib.hash import sha256_crypt
from flask_jwt_extended import (
    get_jwt_identity, jwt_required
)
from app import bp,db
from app.models import User
from datetime import datetime
from core.utils import validate_request_schema


ALLOWED_ROLES = ['admin', 'superadmin']


@bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    if get_jwt_identity().split(":")[1] not in ALLOWED_ROLES:
        abort(401, "Unauthorized to access this resource")
    users = []
    for user in User.query.all():
        u = {
            "uuid": user.uuid,
            "name": user.name,
            "username": user.username,
            "role": user.role,
            "birthday": user.birthday,
            "phone_number": user.phone_number,
            "status": user.status
            }
        users.append(u)
    return jsonify(users)


@bp.route('/user', methods=['GET'])
@jwt_required()
def get_user_profile():
    doctor = User.query.filter_by(username= get_jwt_identity().split(":")[0]).\
        first_or_404(description="User doesn't exist")
    return jsonify(doctor.serialize())


@bp.route('/user', methods=['POST'])
def create_user():
    schema = {
        'username': {'type': 'string', 'required': True, 'empty': False},
        'password': {'type': 'string', 'required': True, 'empty': False},
        'name': {'type': 'string', 'required': True, 'empty': False},
        'birthday': {'type': 'string', 'required': True, 'empty': False},
        'phone_number': {'type': 'string', 'required': True, 'empty': False},
        'role': {'type': 'string', 'required': True, 'empty': False,
        'allowed': ['admin', 'doctor', 'reception', 'pharmacist','analist']}
    }

    validate_request_schema(schema, request.json)

    # validate if the chosen username is already in use
    if User.query.filter_by(username=request.json['username']).first():
        abort(409, "Username is already in use")
    
        # trim spaces in username
    request.json['username'] = request.json['username'].replace(" ", "").lower()
    # hash the doctor password
    request.json['password'] = sha256_crypt.encrypt(str(request.json.get('password')))
    new_user = User.deserialize(request.json)

    new_user.role = request.json['role']
    new_user.action_author = 'get_jwt_identity().split(":")[0]'
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.serialize()), 201


@bp.route('/user', methods=['PUT'])
@jwt_required()
def update_user_profile():
    if get_jwt_identity().split(":")[1] not in ALLOWED_ROLES:
        abort(401, "Unauthorized to access this resource")

    uuid = request.args.get('uuid')
    
    if not uuid:
        abort(400, "uuid param is missing")

    schema = {
        'name': {'type': 'string', 'required': True, 'empty': False},
        'birthday': {'type': 'string', 'required': True, 'empty': False},
        'phone_number': {'type': 'string', 'required': True, 'empty': False},
        'role': {'type': 'string', 'required': True, 'empty': False,
        'allowed': ['superadmin','admin', 'doctor', 'reception', 'pharmacist','analist']}
    }

    validate_request_schema(schema, request.json)

    user = User.query.filter_by(uuid=uuid).\
        first_or_404(description='Invalid uuid supplied')
    
    
    user.name = request.json['name']
    user.phone_number = request.json['phone_number']
    user.role = request.json['role']
    user.action_author = get_jwt_identity().split(":")[0]
    user.updated = datetime.utcfromtimestamp(datetime.now().timestamp() + 7200). \
        strftime('%Y-%m-%d %H:%M:%S')
    db.session.commit()
    return jsonify(user.serialize())
