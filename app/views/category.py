from hashlib import new
from flask import jsonify, request,Blueprint
from werkzeug.exceptions import abort
from passlib.hash import sha256_crypt
from flask_jwt_extended import (
    get_jwt_identity, jwt_required
)
from app import bp,db
from app.models import Category
from datetime import datetime
from core.utils import validate_request_schema


ALLOWED_ROLES = ['admin', 'superadmin']


@bp.route('/categories', methods=['GET'])
@jwt_required()
def get_all_categories():
    if get_jwt_identity().split(":")[1] not in ALLOWED_ROLES:
        abort(401, "Unauthorized to access this resource")

    categories = []
    for category in Category.query.all():
        u = {
            "uuid": category.uuid,
            "name": category.name
            }
        categories.append(u)
    return jsonify(categories)


@bp.route('/category', methods=['GET'])
@jwt_required()
def get_one_category():
    if get_jwt_identity().split(":")[1] not in ALLOWED_ROLES:
        abort(401, "Unauthorized to access this resource")

    uuid = request.args.get('uuid')
    
    if not uuid:
        abort(400, "uuid param is missing")

    category = Category.query.filter_by(uuid=uuid).\
        first_or_404(description='Invalid uuid supplied')
    u = {
            "uuid": category.uuid,
            "name": category.name,
            "products": category.products
            }
    
    return jsonify(u)


@bp.route('/category', methods=['POST'])
@jwt_required()
def create_csategory():
    if get_jwt_identity().split(":")[1] not in ALLOWED_ROLES:
        abort(401, "Unauthorized to access this resource")

    schema = {
        'name': {'type': 'string', 'required': True, 'empty': False}
    }

    validate_request_schema(schema, request.json)

    # validate if the chosen name is already in use
    if Category.query.filter_by(name=request.json['name']).first():
        abort(409, "name is already in use")
    
    new_object = Category.deserialize(request.json)

    new_object.action_author = get_jwt_identity().split(":")[0]
    db.session.add(new_object)
    db.session.commit()
    return jsonify(new_object.serialize()), 201


@bp.route('/category', methods=['PUT'])
@jwt_required()
def edit_category():
    if get_jwt_identity().split(":")[1] not in ALLOWED_ROLES:
        abort(401, "Unauthorized to access this resource")
    
    schema = {
        'name': {'type': 'string', 'required': True, 'empty': False}
    }

    validate_request_schema(schema, request.json)

    uuid = request.args.get('uuid')
    
    if not uuid:
        abort(400, "uuid param is missing")

    category = Category.query.filter_by(uuid=uuid).\
        first_or_404(description='Invalid uuid supplied')

    if category.name != request.json['name']:
        if Category.query.filter(Category.name == request.json['name'], Category.uuid != category.uuid).first():
            abort(409, "name is already in use")

    category.name = request.json['name']

    category.action_author = get_jwt_identity().split(":")[0]
    category.updated = datetime.utcfromtimestamp(datetime.now().timestamp() + 7200). \
            strftime('%Y-%m-%d %H:%M:%S')    

    db.session.commit()

    return jsonify(category.serialize()), 201
