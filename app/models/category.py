from app import db
from core.utils import generate_local_timestamp
from uuid import uuid4

class Category(db.Model):
    uuid = db.Column(db.String(50), primary_key=True, default=lambda: uuid4().hex)
    name = db.Column(db.String(50), nullable=False)
    
    
    products = db.relationship('Product', secondary='product_category_association',
                               back_populates='categories', overlaps="category,products")

    created = db.Column(db.DateTime, nullable=False, default=lambda: generate_local_timestamp())
    updated = db.Column(db.DateTime, nullable=False, default=lambda: generate_local_timestamp())
    action_author = db.Column(db.String(50), nullable=False)
    
    def __repr__(self):
        return f"<category {self.uuid}  >"

    def serialize(self):
        return {
            "uuid": self.uuid,
            "name": self.name
        }

    @staticmethod
    def deserialize(request_json):
        return Category(
            name = request_json['name']
        )
