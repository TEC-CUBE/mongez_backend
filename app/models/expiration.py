from app import db
from core.utils import generate_local_timestamp
from uuid import uuid4

class Expiration(db.Model):
    uuid = db.Column(db.String(50), primary_key=True, default=lambda: uuid4().hex)
    product_uuid = db.Column(db.String(50), db.ForeignKey('product.uuid'))
    date = db.Column(db.Date, nullable=False)
    stock = db.Column(db.Float(), default=0)
    
    deleted_at = db.Column(db.DateTime, nullable=True)
    created = db.Column(db.DateTime, nullable=False, default=lambda: generate_local_timestamp())
    updated = db.Column(db.DateTime, nullable=False, default=lambda: generate_local_timestamp())
    action_author = db.Column(db.String(50), nullable=False)
    
    def __repr__(self):
        return f"<product {self.uuid} {self.name} {self.status} >"

    def serialize(self):
        return {
            "uuid": self.uuid,
            "date": self.date,
            "stock": self.stock,
        }

    @staticmethod
    def deserialize(request_json):
        return Expiration(
            
        )
