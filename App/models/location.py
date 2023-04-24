from flask_login import UserMixin
from sqlalchemy.sql.expression import func

class Location(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Integer, nullable=False)
    longitude = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    active = db.Column(db.Boolean, default=False)

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def toJson(self):
        return{
            "id": self.id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "name": self.name
        }

    def __repr__(self):
        return f'<Location: {self.id} | {self.latitude} | {self.longitude} | {self.name} | {"active" if self.active else "not active"}>'

class LocationCategory(db.Model):
    __tabelename__= 'location_category'
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    last_modified = db.Column(db.DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f'<Location Category last modified {self.last_modified.strftime("%Y/%m/%d, %H:%m:%s")}'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    location_name = db.Column(db.String(200), nullable=False)
    location = db.relationship('Location', secondary='location_category', backref=db.backef('categories'), lazy=True)

    def __init__(self, location_id, location_name):
        self.location_id = location_id
        self.location_name = location_name

    def __repr__(self):
        return f'<Location Category: {self.id} - {self.location_name}>'

    def toJson(self):
        return{
            "id": self.id,
            "location_id": self.location_id,
            "location_name": self.location_name
        }