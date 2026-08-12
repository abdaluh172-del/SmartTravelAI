from flask import Blueprint, jsonify
from models import Destination

destinations_bp = Blueprint("destinations", __name__)


@destinations_bp.route("/api/destinations", methods=["GET"])
def list_destinations():
    destinations = Destination.query.all()
    return jsonify([d.to_dict() for d in destinations])


@destinations_bp.route("/api/destinations/<code>", methods=["GET"])
def get_destination(code):
    dest = Destination.query.filter_by(airport_code=code.upper()).first()
    if not dest:
        return jsonify({"error": "الوجهة غير موجودة"}), 404
    return jsonify(dest.to_dict())
