from flask import Blueprint, request, jsonify
from app.models.intento import Intento, Respuesta

intento_bp = Blueprint("intentos", __name__)

@intento_bp.route("/", methods=["POST"])
def crear_intento():
    """Crear un nuevo intento"""
    try:
        data = request.json
        intento = Intento(**data)
        intento.save()
        return jsonify({"msg": "Intento creado exitosamente", "intento_id": intento.intento_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@intento_bp.route("/", methods=["GET"])
def listar_intentos():
    """Listar todos los intentos"""
    try:
        intentos = Intento.objects()
        return jsonify([intento.to_mongo().to_dict() for intento in intentos]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@intento_bp.route("/<intento_id>", methods=["GET"])
def obtener_intento(intento_id):
    """Obtener un intento específico"""
    try:
        intento = Intento.objects(intento_id=intento_id).first()
        if not intento:
            return jsonify({"error": "Intento no encontrado"}), 404
        return jsonify(intento.to_mongo().to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@intento_bp.route("/<intento_id>", methods=["PUT"])
def actualizar_intento(intento_id):
    """Actualizar un intento"""
    try:
        data = request.json
        intento = Intento.objects(intento_id=intento_id).first()
        if not intento:
            return jsonify({"error": "Intento no encontrado"}), 404
        
        intento.update(**data)
        return jsonify({"msg": "Intento actualizado exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@intento_bp.route("/alumno/<alumno_id>", methods=["GET"])
def listar_intentos_alumno(alumno_id):
    """Listar intentos de un alumno específico"""
    try:
        intentos = Intento.objects(alumno_id=alumno_id)
        return jsonify([intento.to_mongo().to_dict() for intento in intentos]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@intento_bp.route("/evaluacion/<evaluacion_id>", methods=["GET"])
def listar_intentos_evaluacion(evaluacion_id):
    """Listar intentos de una evaluación específica"""
    try:
        intentos = Intento.objects(evaluacion_id=evaluacion_id)
        return jsonify([intento.to_mongo().to_dict() for intento in intentos]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@intento_bp.route("/<intento_id>/finalizar", methods=["PUT"])
def finalizar_intento(intento_id):
    """Finalizar un intento y calcular calificación"""
    try:
        data = request.json
        intento = Intento.objects(intento_id=intento_id).first()
        if not intento:
            return jsonify({"error": "Intento no encontrado"}), 404
        
        # Calcular calificación (ejemplo básico)
        respuestas_correctas = sum(1 for respuesta in data.get('respuestas', []) if respuesta.get('es_correcta', False))
        total_preguntas = len(data.get('respuestas', []))
        calificacion = int((respuestas_correctas / total_preguntas) * 20) if total_preguntas > 0 else 0
        
        intento.update(
            estado="finalizado",
            calificacion=calificacion,
            fecha_fin=data.get('fecha_fin'),
            respuestas=data.get('respuestas', [])
        )
        
        return jsonify({
            "msg": "Intento finalizado exitosamente",
            "calificacion": calificacion
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400