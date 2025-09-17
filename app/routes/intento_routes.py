from flask import Blueprint, request, jsonify
from app.models.intento import Intento, Respuesta
from app.models.evaluacion import Evaluacion # Needed to get correct answers
import uuid
from datetime import datetime

intento_bp = Blueprint("intentos", __name__)

@intento_bp.route("/", methods=["POST"])
def crear_intento():
    """Crea un nuevo intento para una evaluación."""
    try:
        data = request.get_json()

        required_fields = ["evaluacion_id", "alumno_id"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Campos requeridos faltantes: evaluacion_id, alumno_id"}), 400

        # Crear el intento inicial (sin respuestas)
        intento_id = str(uuid.uuid4())
        nuevo_intento = Intento(
            intento_id=intento_id,
            evaluacion_id=data["evaluacion_id"],
            alumno_id=data["alumno_id"]
        )

        nuevo_intento.save()
        return jsonify(nuevo_intento.to_json()), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@intento_bp.route("/<string:intento_id>/finalizar", methods=["PUT"])
def finalizar_intento(intento_id):
    """Finaliza un intento, envía las respuestas y calcula la calificación."""
    try:
        data = request.get_json()
        respuestas_data = data.get("respuestas", [])

        intento = Intento.find_by_id(intento_id)
        if not intento:
            return jsonify({"error": "Intento no encontrado"}), 404

        evaluacion = Evaluacion.find_by_id(intento["evaluacion_id"])
        if not evaluacion:
            return jsonify({"error": "Evaluación asociada no encontrada"}), 404
        
        # Crear un mapa de pregunta_id -> respuesta_correcta para una búsqueda fácil
        mapa_respuestas_correctas = {p["pregunta_id"]: p["respuesta_correcta"] for p in evaluacion["preguntas"]}

        respuestas_obj = []
        respuestas_correctas = 0

        for r_data in respuestas_data:
            pregunta_id = r_data.get("pregunta_id")
            opcion_marcada = r_data.get("opcion_marcada")
            es_correcta = (mapa_respuestas_correctas.get(pregunta_id) == opcion_marcada)
            if es_correcta:
                respuestas_correctas += 1

            respuesta = Respuesta(
                pregunta_id=pregunta_id,
                opcion_marcada=opcion_marcada,
                es_correcta=es_correcta
            )
            respuestas_obj.append(respuesta.to_dict())

        total_preguntas = len(evaluacion["preguntas"])
        calificacion = int((respuestas_correctas / total_preguntas) * 20) if total_preguntas > 0 else 0

        update_data = {
            "estado": "finalizado",
            "calificacion": calificacion,
            "fecha_fin": datetime.utcnow(),
            "respuestas": respuestas_obj
        }

        Intento.update_by_id(intento_id, update_data)

        return jsonify({
            "msg": "Intento finalizado exitosamente",
            "calificacion": calificacion,
            "intento_id": intento_id
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@intento_bp.route("/alumno/<string:alumno_id>", methods=["GET"])
def listar_intentos_alumno(alumno_id):
    """Listar todos los intentos de un alumno."""
    try:
        intentos = Intento.find_by_alumno(alumno_id)
        for intento in intentos:
            if '_id' in intento:
                intento['_id'] = str(intento['_id'])
        return jsonify(intentos), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@intento_bp.route("/<string:intento_id>", methods=["GET"])
def obtener_intento(intento_id):
    """Obtener un intento específico por su ID."""
    try:
        intento = Intento.find_by_id(intento_id)
        if not intento:
            return jsonify({"error": "Intento no encontrado"}), 404
        if '_id' in intento:
            intento['_id'] = str(intento['_id'])
        return jsonify(intento), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500