from app import db
from core.utils import generate_local_timestamp
from uuid import uuid4

class Barcode(db.Model):
    uuid = db.Column(db.String(50), primary_key=True, default=lambda: uuid4().hex)
    product_uuid = db.Column(db.String(50), db.ForeignKey('product.uuid'))
    
    code = db.Column(db.String(50), nullable=False)
    
    created = db.Column(db.DateTime, nullable=False, default=lambda: generate_local_timestamp())
    updated = db.Column(db.DateTime, nullable=False, default=lambda: generate_local_timestamp())
    action_author = db.Column(db.String(50), nullable=False)
    
    def __repr__(self):
        return f"<Barcode {self.uuid} {self.code} >"

    def serialize(self):
        return {
            "uuid": self.uuid,
            "code": self.code
        }

    @staticmethod
    def deserialize(bar):
        return Barcode(
            code = bar
        )
