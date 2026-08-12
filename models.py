import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


def now():
    return datetime.datetime.utcnow()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=now)

    favorites = db.relationship("Favorite", backref="user", lazy=True)
    trip_plans = db.relationship("TripPlan", backref="user", lazy=True)

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat(),
        }


class Airline(db.Model):
    __tablename__ = "airlines"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    name_ar = db.Column(db.String(120))
    logo_url = db.Column(db.String(255))
    provider_key = db.Column(db.String(50), default="mock")
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "name_ar": self.name_ar,
            "logo_url": self.logo_url,
            "is_active": self.is_active,
        }


class Destination(db.Model):
    __tablename__ = "destinations"

    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(120), nullable=False)
    city_ar = db.Column(db.String(120))
    country = db.Column(db.String(120))
    airport_code = db.Column(db.String(10), index=True)
    image_url = db.Column(db.String(255))
    description_ar = db.Column(db.Text)

    def to_dict(self):
        return {
            "id": self.id,
            "city": self.city,
            "city_ar": self.city_ar,
            "country": self.country,
            "airport_code": self.airport_code,
            "image_url": self.image_url,
            "description_ar": self.description_ar,
        }


class SearchLog(db.Model):
    __tablename__ = "search_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    origin = db.Column(db.String(10))
    destination = db.Column(db.String(10))
    depart_date = db.Column(db.String(20))
    return_date = db.Column(db.String(20))
    passengers = db.Column(db.Integer, default=1)
    cabin_class = db.Column(db.String(30))
    results_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=now)

    def to_dict(self):
        return {
            "id": self.id,
            "origin": self.origin,
            "destination": self.destination,
            "depart_date": self.depart_date,
            "return_date": self.return_date,
            "passengers": self.passengers,
            "cabin_class": self.cabin_class,
            "results_count": self.results_count,
            "created_at": self.created_at.isoformat(),
        }


class TripPlan(db.Model):
    __tablename__ = "trip_plans"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    destination = db.Column(db.String(120))
    days = db.Column(db.Integer)
    budget = db.Column(db.Float)
    trip_type = db.Column(db.String(30))
    interests = db.Column(db.String(255))
    plan_json = db.Column(db.Text)  # JSON serialized itinerary
    is_mock = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=now)

    def to_dict(self):
        import json

        return {
            "id": self.id,
            "destination": self.destination,
            "days": self.days,
            "budget": self.budget,
            "trip_type": self.trip_type,
            "interests": self.interests,
            "plan": json.loads(self.plan_json) if self.plan_json else None,
            "is_mock": self.is_mock,
            "created_at": self.created_at.isoformat(),
        }


class Favorite(db.Model):
    __tablename__ = "favorites"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    item_type = db.Column(db.String(30))  # flight / destination
    item_ref = db.Column(db.String(120))  # flight id or destination code
    item_data = db.Column(db.Text)  # JSON snapshot
    created_at = db.Column(db.DateTime, default=now)

    def to_dict(self):
        import json

        return {
            "id": self.id,
            "item_type": self.item_type,
            "item_ref": self.item_ref,
            "item_data": json.loads(self.item_data) if self.item_data else None,
            "created_at": self.created_at.isoformat(),
        }


class Hotel(db.Model):
    """Placeholder table for future hotel provider integration."""

    __tablename__ = "hotels"

    id = db.Column(db.Integer, primary_key=True)
    destination_code = db.Column(db.String(10), index=True)
    name = db.Column(db.String(160))
    stars = db.Column(db.Integer)
    price_per_night = db.Column(db.Float)
    currency = db.Column(db.String(10), default="SAR")
    provider_key = db.Column(db.String(50), default="mock")

    def to_dict(self):
        return {
            "id": self.id,
            "destination_code": self.destination_code,
            "name": self.name,
            "stars": self.stars,
            "price_per_night": self.price_per_night,
            "currency": self.currency,
        }
