from hashlib import new
from flask import jsonify, request,Blueprint
from werkzeug.exceptions import abort
from passlib.hash import sha256_crypt
from flask_jwt_extended import (
    get_jwt_identity, jwt_required
)
from app import bp,db, Config
from app.models import Product, Category, Barcode, Image
from datetime import datetime
from core.utils import validate_request_schema
from core.image.process import control_image_size, optimize_image
from core.aws.aws_s3 import upload_image, delete_object
import re

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
            "package_price": product.price * product.package,
            "package": product.package,
            "image": product.image.url if product.image else "",
            "date_validity" : product.date_validity if product.date_validity != None else False,
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
        'image': {'type': 'dict', 'schema': 
                  {
                    'name': {'type': 'string'},
                    'type': {'type': 'string'},
                    'base64': {'type': 'string'}
                    }, 'required': False, 'empty': True},
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

    request.json['name'] = re.sub(r'\s+', ' ', request.json['name']).strip()
    if Product.query.filter(Product.name == request.json['name']).first():
            abort(409, "name is already in use by another product")


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

    if 'image' in request.json and request.json['image']:
        image_size_limit = Config.MAX_CONTENT_LENGTH
        image = request.json['image']

        new_image = Image.deserialize(image)
        optimized_image = optimize_image(image['base64'])

        if not control_image_size(image['base64'], image_size_limit):
            abort(400, f"product image exceeded the maximum size limit of {image_size_limit} KB")

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        image_url = upload_image(f"product-image-{timestamp}", optimized_image, Config.S3_BUCKET)

        if not re.match(Config.REGEX, image_url):
            abort(400, "Unable to process the product image")

        new_image.url = image_url
        new_image.action_author = get_jwt_identity().split(":")[0]

        db.session.add(new_image)
        new_image.products.append(new_object)

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
        'image': {'type': 'dict', 'schema': 
                  {
                    'name': {'type': 'string'},
                    'type': {'type': 'string'},
                    'base64': {'type': 'string'}
                    }, 'required': False, 'empty': True},
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
    request.json['name'] = re.sub(r'\s+', ' ', request.json['name']).strip()
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
    
    if 'image' in request.json and request.json['image']:
        image_uuid = product.image.uuid if product.image else ""

        old_image = Image.query.filter_by(uuid=image_uuid).first()

        if old_image:
            delete_object(old_image.url.split('/')[-1], Config.S3_BUCKET)

        image_size_limit = Config.MAX_CONTENT_LENGTH
        image = request.json['image']

        new_image = Image.deserialize(image)
        optimized_image = optimize_image(image['base64'])

        if not control_image_size(image['base64'], image_size_limit):
            abort(400, f"product image exceeded the maximum size limit of {image_size_limit} KB")

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        image_url = upload_image(f"product-image-{timestamp}", optimized_image, Config.S3_BUCKET)

        if not re.match(Config.REGEX, image_url):
            abort(400, "Unable to process the product image")

        new_image.url = image_url
        new_image.action_author = get_jwt_identity().split(":")[0]

        db.session.add(new_image)
        new_image.products.append(product)    
    
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
