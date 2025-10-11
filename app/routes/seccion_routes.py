# app/routes/seccion_route.py
from flask import Blueprint, request, jsonify, current_app
from app.models.seccion import Seccion
from bson.objectid import ObjectId

seccion_bp = Blueprint('seccion_bp', __name__)

@seccion_bp.route('/', methods=['POST'])
def create_seccion():
    data = request.get_json() or {}
    # convertir grado_id a ObjectId si viene como string
    grado_id = data.get('grado_id')
    nueva = Seccion(
        nombre=data.get('nombre'),
        grado_id=grado_id,
        estado=data.get('estado', True)
    )
    # Insertar usando tipos nativos
    current_app.db.secciones.insert_one(nueva.to_dict())
    return jsonify({"mensaje": "Sección creada exitosamente", "id": str(nueva._id)}), 201

@seccion_bp.route('/', methods=['GET'])
def get_secciones():
    secciones = []
    for sdata in current_app.db.secciones.find():
        s = Seccion.from_dict(sdata)
        secciones.append(s.to_json())
    return jsonify(secciones), 200

@seccion_bp.route('/<id>', methods=['GET'])
def get_seccion(id):
    try:
        oid = ObjectId(id)
    except Exception:
        return jsonify({"mensaje":"ID inválido"}), 400
    sdata = current_app.db.secciones.find_one({'_id': oid})
    if sdata:
        s = Seccion.from_dict(sdata)
        return jsonify(s.to_json()), 200
    return jsonify({"mensaje": "Sección no encontrada"}), 404

@seccion_bp.route('/<id>', methods=['PUT','PATCH'])
def update_seccion(id):
    try:
        oid = ObjectId(id)
    except Exception:
        return jsonify({"mensaje":"ID inválido"}), 400
    data = request.get_json() or {}
    # normalizar campos: si grado_id viene, convertirlo
    if 'grado_id' in data:
        try:
            data['grado_id'] = ObjectId(data['grado_id'])
        except Exception:
            return jsonify({"mensaje":"grado_id inválido"}), 400
    # No permitas que el cliente cambie el _id
    data.pop('_id', None)
    result = current_app.db.secciones.update_one({'_id': oid}, {'$set': data})
    if result.matched_count == 0:
        return jsonify({"mensaje":"Sección no encontrada"}), 404
    return jsonify({"mensaje": "Sección actualizada exitosamente", "modified": result.modified_count}), 200

@seccion_bp.route('/<id>', methods=['DELETE'])
def delete_seccion(id):
    try:
        oid = ObjectId(id)
    except Exception:
        return jsonify({"mensaje":"ID inválido"}), 400
    current_app.db.secciones.delete_one({'_id': oid})
    return jsonify({"mensaje": "Sección eliminada exitosamente"}), 200

@seccion_bp.route('/grado/<grado_id>', methods=['GET'])
def get_secciones_by_grado(grado_id):
    try:
        gid = ObjectId(grado_id)
    except Exception:
        return jsonify({"mensaje":"ID de grado inválido"}), 400
    secciones = []
    for sdata in current_app.db.secciones.find({'grado_id': gid}):
        s = Seccion.from_dict(sdata)
        secciones.append(s.to_json())
    return jsonify(secciones), 200