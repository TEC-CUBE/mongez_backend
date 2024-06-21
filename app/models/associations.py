from app import db
from core.utils import generate_local_timestamp
from uuid import uuid4

class ProductWarehouseAssociation(db.Model):
    __tablename__ = 'product_warehouse_association'
    product_uuid = db.Column(db.String(50), db.ForeignKey('product.uuid'), primary_key=True)
    warehouse_uuid = db.Column(db.String(50), db.ForeignKey('warehouse.uuid'), primary_key=True)
    stock = db.Column(db.Float(), default=0)

class ProductCategoryAssociation(db.Model):
    __tablename__ = 'product_category_association'
    product_uuid = db.Column(db.String(50), db.ForeignKey('product.uuid'), primary_key=True)
    category_uuid = db.Column(db.String(50), db.ForeignKey('category.uuid'), primary_key=True)
