from hashlib import new
from flask import jsonify, request,Blueprint
from werkzeug.exceptions import abort
from passlib.hash import sha256_crypt
from flask_jwt_extended import (
    get_jwt_identity, jwt_required
)
from app import bp,db
from app.models import Product, Category, Barcode
from datetime import datetime
from core.utils import validate_request_schema


ALLOWED_ROLES = ['admin', 'superadmin']


@bp.route('/products', methods=['GET'])
@jwt_required()
def get_all_products():
    if get_jwt_identity().split(":")[1] not in ALLOWED_ROLES:
        abort(401, "Unauthorized to access this resource")

    products = [product.serialize() for product in Product.query.all()]

    return jsonify(products)


@bp.route('/product', methods=['GET'])
@jwt_required()
def get_one_product():
    if get_jwt_identity().split(":")[1] not in ALLOWED_ROLES:
        abort(401, "Unauthorized to access this resource")
    uuid = request.args.get('uuid')
    
    if not uuid:
        abort(400, "uuid param is missing")

    product = Product.query.filter_by(uuid=uuid).\
        first_or_404(description='Invalid uuid supplied')
    
    u = {
            "uuid": product.uuid,
            "name": product.name,
            "price": product.price,
            "package": product.package,
            "image": product.image,
            "stock": product.stock,
            "categories": [category.serialize() for category in product.categories],
            "barcodes": [barcode.serialize() for barcode in product.barcodes],
            "warehouses": [warehouse.serialize() for warehouse in product.warehouses]
        }
    
    return jsonify(u)


@bp.route('/product', methods=['POST'])
@jwt_required()
def create_product():
    if get_jwt_identity().split(":")[1] not in ALLOWED_ROLES:
        abort(401, "Unauthorized to access this resource")

    schema = {
        'name': {'type': 'string', 'required': True, 'empty': False},
        'price': {'type': 'string', 'required': True, 'empty': False},
        'package': {'type': 'string', 'required': True, 'empty': False},
        'image': {'type': 'string', 'required': False, 'empty': True},
        'barcodes': {'type': 'list', 'required': True, 'empty': False},
        'categories': {'type': 'list', 'required': True, 'empty': False}
    }

    validate_request_schema(schema, request.json)

    barcode_codes = request.json['barcodes']
    # validate if the chosen name is already in use
    if Barcode.query.filter(Barcode.code.in_(barcode_codes)).all():
        abort(409, "Barcode is already in use")
    
    category_uuids = request.json['categories']
    # validate if the chosen name is already in use
    categories = Category.query.filter(Category.uuid.in_(category_uuids)).all()


    if len(categories) != len(category_uuids):
        abort(400, "Some category UUIDs are invalid")

    new_object = Product.deserialize(request.json)

    new_object.action_author = get_jwt_identity().split(":")[0]
    db.session.add(new_object)

    for code in barcode_codes:
        if len(code) <= 4:
            abort(400, f"Barcode '{code}' must have more than 4 characters or numbers")
        new_barcode = Barcode.deserialize(code)
        new_barcode.action_author = get_jwt_identity().split(":")[0]
        db.session.add(new_barcode)
        new_object.barcodes.append(new_barcode)

    for category in categories:
        new_object.categories.append(category)

    db.session.commit()
    return jsonify(new_object.serialize()), 201


@bp.route('/product', methods=['PUT'])
@jwt_required()
def edit_product():
    if get_jwt_identity().split(":")[1] not in ALLOWED_ROLES:
        abort(401, "Unauthorized to access this resource")
    
    schema = {
        'name': {'type': 'string', 'required': True, 'empty': False},
        'price': {'type': 'string', 'required': True, 'empty': False},
        'package': {'type': 'string', 'required': True, 'empty': False},
        'image': {'type': 'string', 'required': False, 'empty': True},
        'barcodes': {'type': 'list', 'required': True, 'empty': False},
        'categories': {'type': 'list', 'required': True, 'empty': False}
    }

    validate_request_schema(schema, request.json)

    uuid = request.args.get('uuid')
    
    if not uuid:
        abort(400, "uuid param is missing")

    product = Product.query.filter_by(uuid=uuid).\
        first_or_404(description='Invalid uuid supplied')

    barcode_codes = request.json['barcodes']
    category_uuids = request.json['categories']

    # Validate barcodes
    existing_barcodes = Barcode.query.filter(Barcode.code.in_(barcode_codes)).all()
    if any(barcode.product_uuid != product.uuid for barcode in existing_barcodes):
        abort(409, "One or more barcodes are already in use by another product")

    # Validate categories
    categories = Category.query.filter(Category.uuid.in_(category_uuids)).all()
    if len(categories) != len(category_uuids):
        abort(400, "Some category UUIDs are invalid")


    if product.name != request.json['name']:
        if Product.query.filter(Product.name == request.json['name'], Product.uuid != product.uuid).first():
            abort(409, "name is already in use by another product")

    product.name = request.json['name']
    product.price = request.json['price']
    product.package = request.json['package']
    
    current_barcodes = {barcode.code for barcode in product.barcodes}
    new_barcodes = set(barcode_codes)

    # Barcodes to remove
    barcodes_to_remove = current_barcodes - new_barcodes
    for code in barcodes_to_remove:
        barcode_to_remove = Barcode.query.filter_by(code=code, product_uuid=product.uuid).first()
        if barcode_to_remove:
            db.session.delete(barcode_to_remove)


    # Barcodes to add
    barcodes_to_add = new_barcodes - current_barcodes
    
    for code in barcodes_to_add:
        if len(code) <= 4:
            abort(400, f"Barcode '{code}' must have more than 4 characters or numbers")
        new_barcode = Barcode.deserialize(code)
        new_barcode.action_author = get_jwt_identity().split(":")[0]
        db.session.add(new_barcode)
        product.barcodes.append(new_barcode)

    # Update categories
    product.categories.clear()
    product.categories = categories

    product.action_author = get_jwt_identity().split(":")[0]
    product.updated = datetime.utcfromtimestamp(datetime.now().timestamp() + 7200). \
            strftime('%Y-%m-%d %H:%M:%S')    

    db.session.commit()

    return jsonify(product.serialize()), 201

@bp.route('/product/deactivate', methods=['PUT'])
@jwt_required()
def deactivate_product():
    if get_jwt_identity().split(":")[1] not in ALLOWED_ROLES:
        abort(401, "Unauthorized to access this resource")

    uuid = request.args.get('uuid')
    if not uuid:
        abort(400, "uuid param is missing")

    product = Product.query.filter_by(uuid=uuid).\
        first_or_404(description='invalid uuid supplied')

    if product.stock > 0:
        abort(401, "product stock > 0")

    product.status = "Inactive"
    product.action_author = get_jwt_identity().split(":")[0]
    product.updated = datetime.utcfromtimestamp(datetime.now().timestamp() + 7200). \
        strftime('%Y-%m-%d %H:%M:%S')
    db.session.commit()
    return jsonify({"message": "product deactivated successfully"})


@bp.route('/product/activate', methods=['PUT'])
@jwt_required()
def activate_product():
    if get_jwt_identity().split(":")[1] not in ALLOWED_ROLES:
        abort(401, "Unauthorized to access this resource")

    uuid = request.args.get('uuid')
    if not uuid:
        abort(400, "uuid param is missing")

    product = Product.query.filter_by(uuid=uuid).\
        first_or_404(description='invalid uuid supplied')

    product.status = "Active"
    product.action_author = get_jwt_identity().split(":")[0]
    product.updated = datetime.utcfromtimestamp(datetime.now().timestamp() + 7200). \
        strftime('%Y-%m-%d %H:%M:%S')
    
    db.session.commit()
    return jsonify({"message": "product activated successfully"})
