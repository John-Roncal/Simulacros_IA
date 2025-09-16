from flask import Blueprint, request, jsonify
from app.models.evaluacion import Evaluacion, Pregunta

evaluacion_bp = Blueprint("evaluaciones", __name__)

@evaluacion_bp.route("/", methods=["POST"])
def crear_evaluacion():
    """Crear una nueva evaluación"""
    try:
        data = request.json
        evaluacion = Evaluacion(**data)
        evaluacion.save()
        return jsonify({"msg": "Evaluación creada exitosamente", "evaluacion_id": evaluacion.evaluacion_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@evaluacion_bp.route("/", methods=["GET"])
def listar_evaluaciones():
    """Listar todas las evaluaciones"""
    try:
        evaluaciones = Evaluacion.find_all()
        # Convertir ObjectId a string para JSON
        for evaluacion in evaluaciones:
            if '_id' in evaluacion:
                evaluacion['_id'] = str(evaluacion['_id'])
        return jsonify(evaluaciones), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@evaluacion_bp.route("/<evaluacion_id>", methods=["GET"])
def obtener_evaluacion(evaluacion_id):
    """Obtener una evaluación específica"""
    try:
        evaluacion = Evaluacion.objects(evaluacion_id=evaluacion_id).first()
        if not evaluacion:
            return jsonify({"error": "Evaluación no encontrada"}), 404
        return jsonify(evaluacion.to_mongo().to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@evaluacion_bp.route("/<evaluacion_id>", methods=["PUT"])
def actualizar_evaluacion(evaluacion_id):
    """Actualizar una evaluación"""
    try:
        data = request.json
        evaluacion = Evaluacion.objects(evaluacion_id=evaluacion_id).first()
        if not evaluacion:
            return jsonify({"error": "Evaluación no encontrada"}), 404
        
        evaluacion.update(**data)
        return jsonify({"msg": "Evaluación actualizada exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@evaluacion_bp.route("/<evaluacion_id>", methods=["DELETE"])
def eliminar_evaluacion(evaluacion_id):
    """Eliminar una evaluación"""
    try:
        evaluacion = Evaluacion.objects(evaluacion_id=evaluacion_id).first()
        if not evaluacion:
            return jsonify({"error": "Evaluación no encontrada"}), 404
        
        evaluacion.delete()
        return jsonify({"msg": "Evaluación eliminada exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@evaluacion_bp.route("/docente/<docente_id>", methods=["GET"])
def listar_evaluaciones_docente(docente_id):
    """Listar evaluaciones de un docente específico"""
    try:
        evaluaciones = Evaluacion.objects(docente_id=docente_id)
        return jsonify([eval.to_mongo().to_dict() for eval in evaluaciones]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@evaluacion_bp.route("/grado/<grado>/seccion/<seccion>", methods=["GET"])
def listar_evaluaciones_grado_seccion(grado, seccion):
    """Listar evaluaciones por grado y sección"""
    try:
        evaluaciones = Evaluacion.objects(grado=grado, seccion=seccion)
        return jsonify([eval.to_mongo().to_dict() for eval in evaluaciones]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400