from flask import Blueprint, jsonify
from app import db
from app.models.grado import Grado
from bson.objectid import ObjectId

grado_bp = Blueprint('grado_bp', __name__)

@grado_bp.route('/', methods=['GET'])
def get_grados():
    grados = []
    for grado_data in db.grados.find():
        grados.append(Grado.from_dict(grado_data).to_dict())
    return jsonify(grados), 200

@grado_bp.route('/<id>', methods=['GET'])
def get_grado(id):
    grado_data = db.grados.find_one({'_id': ObjectId(id)})
    if grado_data:
        grado = Grado.from_dict(grado_data).to_dict()
        return jsonify(grado), 200
    return jsonify({"mensaje": "Grado no encontrado"}), 404