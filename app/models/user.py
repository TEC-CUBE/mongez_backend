from app import db
from core.utils import generate_local_timestamp
from uuid import uuid4

class User(db.Model):
    uuid = db.Column(db.String(50), primary_key=True, default=lambda: uuid4().hex)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(400), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    phone_number = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Active")
    
    branch_uuid = db.Column(db.String(50), db.ForeignKey('branch.uuid'), nullable=True)

    deleted_at = db.Column(db.DateTime, nullable=True)
    created = db.Column(db.DateTime, nullable=False, default=lambda: generate_local_timestamp())
    updated = db.Column(db.DateTime, nullable=False, default=lambda: generate_local_timestamp())
    action_author = db.Column(db.String(50), nullable=False)
    
    def __repr__(self):
        return f"<User {self.uuid} {self.username} {self.name} {self.role} {self.status} {self.balance}" \
            f"{self.birthday} {self.phone_number}>"

    def serialize(self):
        return {
            "uuid": self.uuid,
            "username": self.username,
            "name": self.name,
            "role": self.role,
            "birthday": self.birthday,
            "phone_number": self.phone_number,
            "status": self.status,
            "created": self.created,
            "updated": self.updated,
            "action_author": self.action_author,
        }

    @staticmethod
    def deserialize(request_json):
        return User(
            username=request_json['username'],
            password=request_json['password'],
            name=request_json['name'],
            birthday=request_json['birthday'],
            phone_number=request_json['phone_number'],
            role=request_json['role']
        )
