from flask import Blueprint, request, jsonify
from app.models.evaluacion import Evaluacion, Pregunta
import uuid
from datetime import datetime

evaluacion_bp = Blueprint("evaluaciones", __name__)

@evaluacion_bp.route("/", methods=["POST"])
def crear_evaluacion():
    """Crear una nueva evaluación"""
    try:
        data = request.get_json()

        # Validar campos requeridos
        required_fields = ["titulo", "materia", "grado", "seccion", "docente_id", "preguntas"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo requerido faltante: {field}"}), 400

        # Crear instancias de Pregunta a partir de los datos
        preguntas_data = data.get("preguntas", [])
        preguntas_obj = []
        for p_data in preguntas_data:
            pregunta_id = str(uuid.uuid4())
            pregunta = Pregunta(
                pregunta_id=pregunta_id,
                tipo=p_data.get("tipo"),
                enunciado=p_data.get("enunciado"),
                opciones=p_data.get("opciones", []),
                respuesta_correcta=p_data.get("respuesta_correcta")
            )
            preguntas_obj.append(pregunta)

        # Crear la evaluación
        evaluacion_id = str(uuid.uuid4())
        fecha_entrega_str = data.get("fecha_entrega")
        fecha_entrega = datetime.fromisoformat(fecha_entrega_str) if fecha_entrega_str else None

        nueva_evaluacion = Evaluacion(
            evaluacion_id=evaluacion_id,
            titulo=data["titulo"],
            materia=data["materia"],
            grado=data["grado"],
            seccion=data["seccion"],
            docente_id=data["docente_id"],
            fecha_entrega=fecha_entrega,
            intentos_permitidos=data.get("intentos_permitidos", 1),
            preguntas=preguntas_obj
        )

        nueva_evaluacion.save()
        return jsonify({"msg": "Evaluación creada exitosamente", "evaluacion_id": nueva_evaluacion.evaluacion_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@evaluacion_bp.route("/", methods=["GET"])
def listar_evaluaciones():
    """Listar todas las evaluaciones"""
    try:
        evaluaciones = Evaluacion.find_all()
        for evaluacion in evaluaciones:
            if '_id' in evaluacion:
                evaluacion['_id'] = str(evaluacion['_id'])
        return jsonify(evaluaciones), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@evaluacion_bp.route("/<string:evaluacion_id>", methods=["GET"])
def obtener_evaluacion(evaluacion_id):
    """Obtener una evaluación específica"""
    try:
        evaluacion = Evaluacion.find_by_id(evaluacion_id)
        if not evaluacion:
            return jsonify({"error": "Evaluación no encontrada"}), 404
        if '_id' in evaluacion:
            evaluacion['_id'] = str(evaluacion['_id'])
        return jsonify(evaluacion), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@evaluacion_bp.route("/<string:evaluacion_id>", methods=["PUT"])
def actualizar_evaluacion(evaluacion_id):
    """Actualizar una evaluación"""
    try:
        data = request.json
        result = Evaluacion.update_by_id(evaluacion_id, data)
        if result.matched_count == 0:
            return jsonify({"error": "Evaluación no encontrada"}), 404
        return jsonify({"msg": "Evaluación actualizada exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@evaluacion_bp.route("/<string:evaluacion_id>", methods=["DELETE"])
def eliminar_evaluacion(evaluacion_id):
    """Eliminar una evaluación"""
    try:
        result = Evaluacion.delete_by_id(evaluacion_id)
        if result.deleted_count == 0:
            return jsonify({"error": "Evaluación no encontrada"}), 404
        return jsonify({"msg": "Evaluación eliminada exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@evaluacion_bp.route("/docente/<string:docente_id>", methods=["GET"])
def listar_evaluaciones_docente(docente_id):
    """Listar evaluaciones de un docente específico"""
    try:
        evaluaciones = Evaluacion.find_by_docente(docente_id)
        for evaluacion in evaluaciones:
            if '_id' in evaluacion:
                evaluacion['_id'] = str(evaluacion['_id'])
        return jsonify(evaluaciones), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@evaluacion_bp.route("/grado/<string:grado>/seccion/<string:seccion>", methods=["GET"])
def listar_evaluaciones_grado_seccion(grado, seccion):
    """Listar evaluaciones por grado y sección"""
    try:
        evaluaciones = Evaluacion.find_by_grado_seccion(grado, seccion)
        for evaluacion in evaluaciones:
            if '_id' in evaluacion:
                evaluacion['_id'] = str(evaluacion['_id'])
        return jsonify(evaluaciones), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500