from app import db
from core.utils import generate_local_timestamp
from uuid import uuid4

class Warehouse(db.Model):
    uuid = db.Column(db.String(50), primary_key=True, default=lambda: uuid4().hex)
    name = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    
    branch_uuid = db.Column(db.String(50), db.ForeignKey('branch.uuid'), nullable=False)

    created = db.Column(db.DateTime, nullable=False, default=lambda: generate_local_timestamp())
    updated = db.Column(db.DateTime, nullable=False, default=lambda: generate_local_timestamp())
    action_author = db.Column(db.String(50), nullable=False)
    
    def __repr__(self):
        return f"<category {self.uuid}  >"

    def serialize(self):
        return {
            
        }

    @staticmethod
    def deserialize(request_json):
        return Warehouse(
            
        )
