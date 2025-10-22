from flask import Blueprint, request, jsonify
from app.models.intento import Intento, Respuesta
from app.models.evaluacion import Evaluacion
from app.gemini import generar_feedback_ia
import uuid
from datetime import datetime
import json

intento_bp = Blueprint("intentos", __name__)

@intento_bp.route("", methods=["POST"])
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
    """Finaliza un intento, envía las respuestas, calcula la calificación y genera feedback con IA."""
    try:
        data = request.get_json()
        respuestas_data = data.get("respuestas", [])

        intento = Intento.find_by_id(intento_id)
        if not intento:
            return jsonify({"error": "Intento no encontrado"}), 404

        evaluacion = Evaluacion.find_by_id(intento["evaluacion_id"])
        if not evaluacion:
            return jsonify({"error": "Evaluación asociada no encontrada"}), 404
        
        mapa_respuestas_correctas = {p["pregunta_id"]: p["respuesta_correcta"] for p in evaluacion["preguntas"] if "pregunta_id" in p}

        respuestas_obj = []
        respuestas_correctas = 0
        detalle_respuestas_prompt = []

        for r_data in respuestas_data:
            pregunta_id = r_data.get("pregunta_id")
            opcion_marcada = r_data.get("opcion_marcada")

            pregunta_info = next((p for p in evaluacion["preguntas"] if p["pregunta_id"] == pregunta_id), None)
            if not pregunta_info:
                continue

            es_correcta = (mapa_respuestas_correctas.get(pregunta_id) == opcion_marcada)
            if es_correcta:
                respuestas_correctas += 1

            respuesta = Respuesta(
                pregunta_id=pregunta_id,
                opcion_marcada=opcion_marcada,
                es_correcta=es_correcta
            )
            respuestas_obj.append(respuesta)

            detalle_respuestas_prompt.append({
                "pregunta": pregunta_info["enunciado"],
                "respuesta_alumno": opcion_marcada,
                "respuesta_correcta": mapa_respuestas_correctas.get(pregunta_id)
            })

        total_preguntas = len(evaluacion["preguntas"])
        calificacion = int((respuestas_correctas / total_preguntas) * 20) if total_preguntas > 0 else 0

        # Construir el prompt para la IA
        prompt = f"""
        **Contexto:** Eres un asistente de IA para un sistema de gestión educativa. Tu tarea es corregir una evaluación, proporcionar feedback individual para el alumno y un feedback general para el docente. El objetivo es ayudar a la toma de decisiones del profesor.

        **Información de la Evaluación:**
        - **Título:** {evaluacion['titulo']}
        - **Materia:** {evaluacion['materia']}
        - **Grado:** {evaluacion['grado']}
        - **Calificación Obtenida:** {calificacion} / 20

        **Respuestas del Alumno:**
        {json.dumps(detalle_respuestas_prompt, indent=2)}

        **Instrucciones:**
        1.  **Analiza cada respuesta** y determina si es correcta o no.
        2.  **Genera un feedback específico** para cada pregunta, explicando por qué la respuesta es correcta o incorrecta.
        3.  **Genera un feedback general para el alumno,** destacando sus fortalezas y áreas de mejora. Debe ser constructivo y motivador.
        4.  **Genera un feedback para el docente,** resumiendo el desempeño del alumno. Incluye un análisis de las posibles dificultades y sugiere áreas de refuerzo. Este feedback debe ser útil para la toma de decisiones pedagógicas.

        **Formato de Salida (JSON):**
        Quiero que me devuelvas un JSON válido con la siguiente estructura:
        {{
          "feedback_por_pregunta": [
            {{
              "pregunta": "Enunciado de la pregunta 1",
              "feedback": "Feedback específico para la respuesta 1."
            }},
            ...
          ],
          "feedback_alumno": "Feedback general y constructivo para el alumno.",
          "feedback_docente": "Análisis del desempeño y sugerencias para el docente."
        }}
        """

        # Generar feedback con IA
        feedback_json_str = generar_feedback_ia(prompt)
        print(feedback_json_str)

        feedback_alumno_general = "No se pudo generar el feedback."
        feedback_docente_general = "No se pudo generar el feedback."

        if feedback_json_str:
            try:
                # Limpiar la respuesta de la IA
                clean_json_str = feedback_json_str.strip().replace('```json', '').replace('```', '')
                feedback_data = json.loads(clean_json_str)

                feedback_alumno_general = feedback_data.get("feedback_alumno", feedback_alumno_general)
                feedback_docente_general = feedback_data.get("feedback_docente", feedback_docente_general)

                mapa_feedback = {item['pregunta']: item['feedback'] for item in feedback_data.get("feedback_por_pregunta", [])}

                for i, r_obj in enumerate(respuestas_obj):
                    pregunta_info = next((p for p in evaluacion["preguntas"] if p["pregunta_id"] == r_obj.pregunta_id), None)
                    if pregunta_info:
                        r_obj.feedback = mapa_feedback.get(pregunta_info["enunciado"], "No se pudo generar feedback para esta pregunta.")

            except json.JSONDecodeError as e:
                print(f"Error al decodificar el JSON de la IA: {e}")
                # Mantener los feedbacks por defecto

        # Actualizar el intento en la base de datos
        update_data = {
            "estado": "finalizado",
            "calificacion": calificacion,
            "fecha_fin": datetime.utcnow(),
            "respuestas": [r.to_dict() for r in respuestas_obj],
            "feedback_alumno": feedback_alumno_general,
            "feedback_docente": feedback_docente_general
        }

        Intento.update_by_id(intento_id, update_data)

        return jsonify({
            "msg": "Intento finalizado y corregido con IA exitosamente",
            "calificacion": calificacion,
            "intento_id": intento_id,
            "feedback_alumno": feedback_alumno_general
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