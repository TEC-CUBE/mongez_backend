from app import db
from core.utils import generate_local_timestamp
from uuid import uuid4

class Invoice(db.Model):
    uuid = db.Column(db.String(50), primary_key=True, default=lambda: uuid4().hex)
    number = db.Column(db.Integer)
    
    total = db.Column(db.Float(), default=0.00)
    invoice_type = db.Column(db.String(50), nullable=False, default="1")
    sales_man = db.Column(db.String(50), nullable=False)

    details = db.relationship('InvoiceDetails', backref='invoice', lazy=True)

    deleted_at = db.Column(db.DateTime, nullable=True)
    created = db.Column(db.DateTime, nullable=False, default=lambda: generate_local_timestamp())
    updated = db.Column(db.DateTime, nullable=False, default=lambda: generate_local_timestamp())
    action_author = db.Column(db.String(50), nullable=False)
    
    
    def __repr__(self):
        return f"<Invoice {self.uuid} " 

    def serialize(self):
        return {
            "uuid": self.uuid,
            "tatal": self.total,
            "sales_man": self.sales_man,
            "created": self.created,
            "number": self.number
        }

    @staticmethod
    def deserialize(request_json):
        return Invoice(
        )
