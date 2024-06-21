from app import db
from core.utils import generate_local_timestamp
from uuid import uuid4
 
class Branch(db.Model):
    uuid = db.Column(db.String(50), primary_key=True, default=lambda: uuid4().hex)
    name = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Active")
    
    warehouses = db.relationship('Warehouse', backref=db.backref('branch', lazy=True))
    users = db.relationship('User', backref=db.backref('branch', lazy=True))
    
    created = db.Column(db.DateTime, nullable=False, default=lambda: generate_local_timestamp())
    updated = db.Column(db.DateTime, nullable=False, default=lambda: generate_local_timestamp())
    action_author = db.Column(db.String(50), nullable=False)
    
    def __repr__(self):
        return f"<Branch {self.uuid}  >"

    def serialize(self):
        user = []
        for u in self.users:
            item = {
                "uuid": u.uuid ,
                "name": u.name ,
                "role": u.role ,
                "status": u.status
            }
            user.append(item)
        return {
            "uuid": self.uuid,
            "name": self.name,
            "location": self.location,
            "warehouses": self.warehouses,
            "users": user,
            "status": self.status
        }

    @staticmethod
    def deserialize(request_json):
        return Branch(
            name = request_json['name'],
            location = request_json['location']
        )
