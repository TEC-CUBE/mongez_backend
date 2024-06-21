from hashlib import new
from flask import jsonify, request,Blueprint
from werkzeug.exceptions import abort
from passlib.hash import sha256_crypt
from flask_jwt_extended import (
    get_jwt_identity, jwt_required
)
from app import bp,db
from app.models import Branch, User
from datetime import datetime
from core.utils import validate_request_schema


ALLOWED_ROLES = ['admin', 'superadmin']


@bp.route('/branches', methods=['GET'])
@jwt_required()
def get_all_branches():
    if get_jwt_identity().split(":")[1] not in ALLOWED_ROLES:
        abort(401, "Unauthorized to access this resource")

    branches = []
    for branch in Branch.query.all():
        u = {
            "uuid": branch.uuid,
            "name": branch.name,
            "location": branch.location,
            "status": branch.status
            }
        branches.append(u)
    return jsonify(branches)


@bp.route('/branch', methods=['GET'])
@jwt_required()
def get_one_branch():
    if get_jwt_identity().split(":")[1] not in ALLOWED_ROLES:
        abort(401, "Unauthorized to access this resource")

    uuid = request.args.get('uuid')
    
    if not uuid:
        abort(400, "uuid param is missing")

    branch = Branch.query.filter_by(uuid=uuid).\
        first_or_404(description='Invalid uuid supplied')
    u = {
            "uuid": branch.uuid,
            "name": branch.name,
            "location": branch.location,
            "warehouses": branch.warehouses,
            "users": branch.users,
            "status": branch.status
            }
    
    return jsonify(u)


@bp.route('/branch', methods=['POST'])
@jwt_required()
def create_branch():
    if get_jwt_identity().split(":")[1] not in ALLOWED_ROLES:
        abort(401, "Unauthorized to access this resource")

    schema = {
        'name': {'type': 'string', 'required': True, 'empty': False},
        'location': {'type': 'string', 'required': True, 'empty': False}
    }

    validate_request_schema(schema, request.json)

    # validate if the chosen name is already in use
    if Branch.query.filter_by(name=request.json['name']).first():
        abort(409, "name is already in use")
    
    new_object = Branch.deserialize(request.json)

    new_object.action_author = get_jwt_identity().split(":")[0]
    db.session.add(new_object)
    db.session.commit()
    return jsonify(new_object.serialize()), 201


@bp.route('/branch', methods=['PUT'])
@jwt_required()
def edit_branch():
    if get_jwt_identity().split(":")[1] not in ALLOWED_ROLES:
        abort(401, "Unauthorized to access this resource")
    
    schema = {
        'name': {'type': 'string', 'required': True, 'empty': False},
        'location': {'type': 'string', 'required': True, 'empty': False}
    }

    validate_request_schema(schema, request.json)

    uuid = request.args.get('uuid')
    
    if not uuid:
        abort(400, "uuid param is missing")

    branch = Branch.query.filter_by(uuid=uuid).\
        first_or_404(description='Invalid uuid supplied')

    if branch.name != request.json['name']:
        if Branch.query.filter(Branch.name == request.json['name'], Branch.uuid != branch.uuid).first():
            abort(409, "name is already in use")

    branch.name = request.json['name']
    branch.location = request.json['location']

    branch.action_author = get_jwt_identity().split(":")[0]
    branch.updated = datetime.utcfromtimestamp(datetime.now().timestamp() + 7200). \
            strftime('%Y-%m-%d %H:%M:%S')    

    db.session.commit()

    return jsonify(branch.serialize()), 201


@bp.route('/branch/users/add', methods=['POST'])
@jwt_required()
def add_users_to_branch():
    if get_jwt_identity().split(":")[1] not in ALLOWED_ROLES:
        abort(401, "Unauthorized to access this resource")

    schema = {
        'branch': {'type': 'string', 'required': True, 'empty': False},
        'users': {'type': 'list', 'required': True, 'empty': False}
    }

    validate_request_schema(schema, request.json)

    branch = Branch.query.filter_by(uuid=request.json['branch']).\
        first_or_404(description='Invalid uuid supplied')
    
    user_uuids = request.json['users']
    
    users = User.query.filter(User.uuid.in_(user_uuids)).all()

    # Check if all provided users exist
    if len(users) != len(user_uuids):
        abort(400, "Some user UUIDs are invalid")

    for user in users:
        branch.users.append(user)
        # Add the action author to the new object
        user.action_author = get_jwt_identity().split(":")[0]
        user.updated = datetime.utcfromtimestamp(datetime.now().timestamp() + 7200). \
            strftime('%Y-%m-%d %H:%M:%S')

    branch.action_author = get_jwt_identity().split(":")[0]
    branch.updated = datetime.utcfromtimestamp(datetime.now().timestamp() + 7200). \
            strftime('%Y-%m-%d %H:%M:%S')
    db.session.commit()

    return jsonify(branch.serialize()), 201


@bp.route('/branch/deactivate', methods=['PUT'])
@jwt_required()
def deactivate_branch():
    if get_jwt_identity().split(":")[1] not in ALLOWED_ROLES:
        abort(401, "Unauthorized to access this resource")

    uuid = request.args.get('uuid')
    if not uuid:
        abort(400, "uuid param is missing")

    branch = Branch.query.filter_by(uuid=uuid).\
        first_or_404(description='invalid uuid supplied')

    branch.status = "Inactive"
    branch.action_author = get_jwt_identity().split(":")[0]
    branch.updated = datetime.utcfromtimestamp(datetime.now().timestamp() + 7200). \
        strftime('%Y-%m-%d %H:%M:%S')
    db.session.commit()
    return jsonify({"message": "branch deactivated successfully"})


@bp.route('/branch/activate', methods=['PUT'])
@jwt_required()
def activate_branch():
    if get_jwt_identity().split(":")[1] not in ALLOWED_ROLES:
        abort(401, "Unauthorized to access this resource")

    uuid = request.args.get('uuid')
    if not uuid:
        abort(400, "uuid param is missing")

    branch = Branch.query.filter_by(uuid=uuid).\
        first_or_404(description='invalid uuid supplied')

    branch.status = "Active"
    branch.action_author = get_jwt_identity().split(":")[0]
    branch.updated = datetime.utcfromtimestamp(datetime.now().timestamp() + 7200). \
        strftime('%Y-%m-%d %H:%M:%S')
    
    db.session.commit()
    return jsonify({"message": "branch activated successfully"})
