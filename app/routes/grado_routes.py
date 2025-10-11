from flask import Blueprint, jsonify, current_app
from app.models.grado import Grado
from bson.objectid import ObjectId

grado_bp = Blueprint('grado_bp', __name__)

@grado_bp.route('/', methods=['GET'])
def get_grados():
    grados = []
    for grado_data in current_app.db.grados.find():
        grado = Grado.from_dict(grado_data)
        grados.append(grado.to_json())
    return jsonify(grados), 200

@grado_bp.route('/<id>', methods=['GET'])
def get_grado(id):
    try:
        oid = ObjectId(id)
    except Exception:
        return jsonify({"mensaje":"ID inválido"}), 400

    grado_data = current_app.db.grados.find_one({'_id': oid})
    if grado_data:
        grado = Grado.from_dict(grado_data)
        return jsonify(grado.to_json()), 200
    return jsonify({"mensaje": "Grado no encontrado"}), 404