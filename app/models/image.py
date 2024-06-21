from app import db
from core.utils import generate_local_timestamp
from uuid import uuid4


class Image(db.Model):
    uuid = db.Column(db.String(50), primary_key=True, default=lambda: uuid4().hex)
    name = db.Column(db.String(50))
    url = db.Column(db.String(250))
    type = db.Column(db.String(50))
    status = db.Column(db.String(20), nullable=False, default="Active")

    products = db.relationship('Product', backref='image', lazy=True)

    created = db.Column(db.DateTime, nullable=False, default=lambda: generate_local_timestamp())
    updated = db.Column(db.DateTime, nullable=False, default=lambda: generate_local_timestamp())
    action_author = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<Image {self.uuid} {self.name} {self.description} {self.url} {self.status}>"

    def serialize(self):
        return {
            "uuid": self.uuid,
            "name": self.name,
            "url": self.url,
            "status": self.status,
            "created": self.created,
            "updated": self.updated,
            "action_author": self.action_author
        }

    @staticmethod
    def deserialize(request_json):
        return Image(
            name=request_json['name'],
            type=request_json['type']
        )