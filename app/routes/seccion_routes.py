from flask import Blueprint, request, jsonify
from app import db
from app.models.seccion import Seccion
from bson.objectid import ObjectId

seccion_bp = Blueprint('seccion_bp', __name__)

@seccion_bp.route('/', methods=['POST'])
def create_seccion():
    data = request.get_json()
    nueva_seccion = Seccion(
        nombre=data['nombre'],
        grado_id=data['grado_id'],
        estado=data.get('estado', True)
    )
    db.secciones.insert_one(nueva_seccion.to_dict())
    return jsonify({"mensaje": "Sección creada exitosamente"}), 201

@seccion_bp.route('/', methods=['GET'])
def get_secciones():
    secciones = []
    for seccion_data in db.secciones.find():
        secciones.append(Seccion.from_dict(seccion_data).to_dict())
    return jsonify(secciones), 200

@seccion_bp.route('/<id>', methods=['GET'])
def get_seccion(id):
    seccion_data = db.secciones.find_one({'_id': ObjectId(id)})
    if seccion_data:
        seccion = Seccion.from_dict(seccion_data).to_dict()
        return jsonify(seccion), 200
    return jsonify({"mensaje": "Sección no encontrada"}), 404

@seccion_bp.route('/<id>', methods=['PUT'])
def update_seccion(id):
    data = request.get_json()
    db.secciones.update_one({'_id': ObjectId(id)}, {'$set': data})
    return jsonify({"mensaje": "Sección actualizada exitosamente"}), 200

@seccion_bp.route('/<id>', methods=['DELETE'])
def delete_seccion(id):
    db.secciones.delete_one({'_id': ObjectId(id)})
    return jsonify({"mensaje": "Sección eliminada exitosamente"}), 200

@seccion_bp.route('/grado/<grado_id>', methods=['GET'])
def get_secciones_by_grado(grado_id):
    secciones = []
    for seccion_data in db.secciones.find({'grado_id': grado_id}):
        secciones.append(Seccion.from_dict(seccion_data).to_dict())
    return jsonify(secciones), 200