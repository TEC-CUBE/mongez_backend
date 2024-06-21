from flask import Flask, Blueprint, make_response, jsonify
from flask_cors import CORS
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from passlib.hash import sha256_crypt
from flask_migrate import Migrate
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('netcube.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

app = Flask(__name__)
bp = Blueprint('/', __name__, url_prefix='/')
app.config.from_object(Config)
db = SQLAlchemy(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

CORS(
    app,
    origins="*",
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Access-Control-Allow-Credentials",
        "x-*",
        "x-access-token",
        "x-refresh-token"
    ],
    supports_credentials=True
)

from app.views import authentication, user, branch, product, category
from app import errors
from app.models import Barcode, Branch, Category, Expiration, Image, Invoice, InvoiceDetails, Product, associations, Supplier, User, Warehouse

app.register_blueprint(bp)


@app.route('/root')
def index():
    return jsonify({"message": "app working"})

app.register_error_handler(405, lambda e: make_response(jsonify({

    "errors": [
        {
            "reason": "Method not allowed",
            "message": "Request method is not allowed by the server.",
            "code": 405
        }
    ]
}), 405))

app.register_error_handler(500, lambda e: make_response(jsonify({
    "errors": [
        {
            "message": "Internal Server Error",
            "code": 500
        }
    ]
}), 500))
