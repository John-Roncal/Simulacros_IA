from flask import Blueprint, request, jsonify
from app.models.materia import Materia

materia_bp = Blueprint("materias", __name__)

@materia_bp.route("/", methods=["POST"])
def crear_materia():
    try:
        data = request.json
        if "nombre" not in data:
            return jsonify({"error": "El campo 'nombre' es requerido"}), 400

        nueva_materia = Materia(nombre=data["nombre"])
        nueva_materia.save()
        return jsonify(nueva_materia.to_json()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@materia_bp.route("/", methods=["GET"])
def listar_materias():
    try:
        materias = Materia.find_all()
        return jsonify([materia.to_json() for materia in materias]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@materia_bp.route("/<int:materia_id>", methods=["GET"])
def obtener_materia(materia_id):
    try:
        materia = Materia.find_by_id(materia_id)
        if not materia:
            return jsonify({"error": "Materia no encontrada"}), 404
        return jsonify(materia.to_json()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@materia_bp.route("/<int:materia_id>", methods=["PUT"])
def actualizar_materia(materia_id):
    try:
        data = request.json
        result = Materia.update_by_id(materia_id, data)
        if result.matched_count == 0:
            return jsonify({"error": "Materia no encontrada"}), 404
        return jsonify({"msg": "Materia actualizada exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@materia_bp.route("/<int:materia_id>", methods=["DELETE"])
def anular_materia(materia_id):
    try:
        result = Materia.update_by_id(materia_id, {"estado": "inactivo"})
        if result.matched_count == 0:
            return jsonify({"error": "Materia no encontrada"}), 404
        return jsonify({"msg": "Materia anulada exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
