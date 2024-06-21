from app import db
from core.utils import generate_local_timestamp
from uuid import uuid4

class Product(db.Model):
    uuid = db.Column(db.String(50), primary_key=True, default=lambda: uuid4().hex)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float(), default=0.00)
    package = db.Column(db.Integer(), default=1)
    image = db.Column(db.String(250), nullable=True)
    stock = db.Column(db.Float(), default=0)

    status = db.Column(db.String(20), nullable=False, default="Active")

    barcodes = db.relationship('Barcode', backref='product', lazy=True)
    
    warehouses = db.relationship('Warehouse', secondary='product_warehouse_association',
                                  backref=db.backref('product', lazy=True))
    
    categories = db.relationship('Category', secondary='product_category_association',
                                 back_populates='products', overlaps="category,products")
    
    deleted_at = db.Column(db.DateTime, nullable=True)
    created = db.Column(db.DateTime, nullable=False, default=lambda: generate_local_timestamp())
    updated = db.Column(db.DateTime, nullable=False, default=lambda: generate_local_timestamp())
    action_author = db.Column(db.String(50), nullable=False)
    
    def __repr__(self):
        return f"<product {self.uuid} {self.name} {self.status} >"

    def serialize(self):
        return {
            "uuid": self.uuid,
            "name": self.name,
            "price": self.price,
            "package": self.package,
            "image": self.image,
            "stock": self.stock,
            "barcodes": [barcode.serialize() for barcode in self.barcodes],
            "categories": [category.serialize() for category in self.categories],
        }

    @staticmethod
    def deserialize(request_json):
        return Product(
            name = request_json['name'],
            price = request_json['price'],
            package = request_json['package']
        )
