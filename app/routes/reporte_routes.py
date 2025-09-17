from flask import Blueprint, request, jsonify
from app.models.reporte import Reporte
import uuid

reporte_bp = Blueprint("reportes", __name__)

@reporte_bp.route("/", methods=["POST"])
def crear_reporte():
    """Crea un nuevo reporte, usualmente después de finalizar un intento."""
    try:
        data = request.get_json()
        
        required_fields = ["intento_id"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Campo requerido faltante: intento_id"}), 400

        reporte_id = str(uuid.uuid4())
        nuevo_reporte = Reporte(
            reporte_id=reporte_id,
            intento_id=data["intento_id"],
            diagnostico_ia=data.get("diagnostico_ia"),
            recomendaciones_ia=data.get("recomendaciones_ia"),
        )
        
        nuevo_reporte.save()
        return jsonify(nuevo_reporte.to_json()), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reporte_bp.route("/intento/<string:intento_id>", methods=["GET"])
def obtener_reporte_por_intento(intento_id):
    """Obtener reporte por ID de intento."""
    try:
        reporte = Reporte.find_by_intento(intento_id)
        if not reporte:
            return jsonify({"error": "Reporte no encontrado para este intento"}), 404
        if '_id' in reporte:
            reporte['_id'] = str(reporte['_id'])
        return jsonify(reporte), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reporte_bp.route("/<string:reporte_id>", methods=["GET"])
def obtener_reporte(reporte_id):
    """Obtener un reporte específico por su ID."""
    try:
        reporte = Reporte.find_by_id(reporte_id)
        if not reporte:
            return jsonify({"error": "Reporte no encontrado"}), 404
        if '_id' in reporte:
            reporte['_id'] = str(reporte['_id'])
        return jsonify(reporte), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reporte_bp.route("/<string:reporte_id>/retroalimentacion", methods=["PUT"])
def agregar_retroalimentacion_docente(reporte_id):
    """Agrega o actualiza la retroalimentación del docente en un reporte."""
    try:
        data = request.get_json()
        if 'retroalimentacion_docente' not in data:
            return jsonify({"error": "Campo requerido faltante: retroalimentacion_docente"}), 400

        update_data = {
            "retroalimentacion_docente": data["retroalimentacion_docente"]
        }
        
        result = Reporte.update_by_id(reporte_id, update_data)
        if result.matched_count == 0:
            return jsonify({"error": "Reporte no encontrado"}), 404

        return jsonify({"msg": "Retroalimentación agregada exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500