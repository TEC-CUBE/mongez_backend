from app import db
from core.utils import generate_local_timestamp
from uuid import uuid4

class InvoiceDetails(db.Model):
    uuid = db.Column(db.String(50), primary_key=True, default=lambda: uuid4().hex)

    product_uuid = db.Column(db.String(50), db.ForeignKey('product.uuid'))
    invoice_uuid = db.Column(db.String(50), db.ForeignKey('invoice.uuid'))


    price = db.Column(db.Float(), default=0.00)
    quantity = db.Column(db.Float(), default=0.00)


    deleted_at = db.Column(db.DateTime, nullable=True)
    created = db.Column(db.DateTime, nullable=False, default=lambda: generate_local_timestamp())
    updated = db.Column(db.DateTime, nullable=False, default=lambda: generate_local_timestamp())
    action_author = db.Column(db.String(50), nullable=False)
    
    def __repr__(self):
        return f"<ProductInvoiceDetails {self.uuid}" 

    def serialize(self):
        return {
            "uuid": self.uuid,
            "price": self.price,
            "quantity": self.quantity,
            "created": self.created,
            "updated": self.updated,
            "action_author": self.action_author
        }

    @staticmethod
    def deserialize(request_json):
        return InvoiceDetails(
            
        )
