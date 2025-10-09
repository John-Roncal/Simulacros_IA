from flask import Blueprint, request, jsonify
from app import db
from app.models.grado import Grado
from bson.objectid import ObjectId

grado_bp = Blueprint('grado_bp', __name__)

@grado_bp.route('/', methods=['POST'])
def create_grado():
    data = request.get_json()
    nuevo_grado = Grado(
        nombre=data['nombre'],
        descripcion=data.get('descripcion'),
        estado=data.get('estado', True)
    )
    db.grados.insert_one(nuevo_grado.to_dict())
    return jsonify({"mensaje": "Grado creado exitosamente"}), 201

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

@grado_bp.route('/<id>', methods=['PUT'])
def update_grado(id):
    data = request.get_json()
    db.grados.update_one({'_id': ObjectId(id)}, {'$set': data})
    return jsonify({"mensaje": "Grado actualizado exitosamente"}), 200

@grado_bp.route('/<id>', methods=['DELETE'])
def delete_grado(id):
    db.grados.delete_one({'_id': ObjectId(id)})
    return jsonify({"mensaje": "Grado eliminado exitosamente"}), 200