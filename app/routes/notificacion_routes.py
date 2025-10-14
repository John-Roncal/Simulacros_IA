from flask import Blueprint, request, jsonify
from app.models.notificacion import Notificacion
import uuid

notificacion_bp = Blueprint('notificaciones', __name__)

@notificacion_bp.route('', methods=['POST'])
def crear_notificacion():
    """Crea una nueva notificación."""
    data = request.get_json()

    if not data or 'usuario_id' not in data or 'mensaje' not in data or 'tipo' not in data:
        return jsonify({"error": "La solicitud debe contener usuario_id, mensaje y tipo."}), 400

    try:
        notificacion_id = str(uuid.uuid4())

        nueva_notificacion = Notificacion(
            notificacion_id=notificacion_id,
            usuario_id=data['usuario_id'],
            mensaje=data['mensaje'],
            tipo=data['tipo']
        )

        nueva_notificacion.save()

        return jsonify(nueva_notificacion.to_json()), 201

    except Exception as e:
        return jsonify({"error": f"Ocurrió un error: {str(e)}"}), 500

@notificacion_bp.route('/usuario/<string:usuario_id>', methods=['GET'])
def obtener_notificaciones_por_usuario(usuario_id):
    """Obtiene todas las notificaciones para un usuario específico."""
    try:
        notificaciones = Notificacion.find_by_usuario(usuario_id)

        results = []
        for notificacion in notificaciones:
            if '_id' in notificacion and not isinstance(notificacion['_id'], str):
                notificacion['_id'] = str(notificacion['_id'])
            results.append(notificacion)

        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": f"Ocurrió un error: {str(e)}"}), 500

@notificacion_bp.route('/<string:notificacion_id>', methods=['PUT'])
def actualizar_notificacion(notificacion_id):
    """Actualiza una notificación (ej. marcar como leída)."""
    data = request.get_json()

    update_data = {}
    if 'estado' in data:
        update_data['estado'] = data['estado']

    if not update_data:
        return jsonify({"error": "No se proporcionaron datos para actualizar."}), 400

    try:
        result = Notificacion.update_by_id(notificacion_id, update_data)

        if result.matched_count == 0:
            return jsonify({"error": "Notificación no encontrada"}), 404

        return jsonify({"msg": "Notificación actualizada exitosamente"}), 200

    except Exception as e:
        return jsonify({"error": f"Ocurrió un error: {str(e)}"}), 500

@notificacion_bp.route('/<string:notificacion_id>', methods=['DELETE'])
def eliminar_notificacion(notificacion_id):
    """Elimina una notificación."""
    try:
        result = Notificacion.delete_by_id(notificacion_id)

        if result.deleted_count == 0:
            return jsonify({"error": "Notificación no encontrada"}), 404

        return jsonify({"msg": "Notificación eliminada exitosamente"}), 200

    except Exception as e:
        return jsonify({"error": f"Ocurrió un error: {str(e)}"}), 500
