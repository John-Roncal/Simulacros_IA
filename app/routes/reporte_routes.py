from flask import Blueprint, request, jsonify
from app.models.reporte import Reporte

reporte_bp = Blueprint("reportes", __name__)

@reporte_bp.route("/", methods=["POST"])
def crear_reporte():
    """Crear un nuevo reporte"""
    try:
        data = request.json
        reporte = Reporte(**data)
        reporte.save()
        return jsonify({"msg": "Reporte creado exitosamente", "reporte_id": reporte.reporte_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@reporte_bp.route("/", methods=["GET"])
def listar_reportes():
    """Listar todos los reportes"""
    try:
        reportes = Reporte.objects()
        return jsonify([reporte.to_mongo().to_dict() for reporte in reportes]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@reporte_bp.route("/<reporte_id>", methods=["GET"])
def obtener_reporte(reporte_id):
    """Obtener un reporte específico"""
    try:
        reporte = Reporte.objects(reporte_id=reporte_id).first()
        if not reporte:
            return jsonify({"error": "Reporte no encontrado"}), 404
        return jsonify(reporte.to_mongo().to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@reporte_bp.route("/<reporte_id>", methods=["PUT"])
def actualizar_reporte(reporte_id):
    """Actualizar un reporte"""
    try:
        data = request.json
        reporte = Reporte.objects(reporte_id=reporte_id).first()
        if not reporte:
            return jsonify({"error": "Reporte no encontrado"}), 404
        
        reporte.update(**data)
        return jsonify({"msg": "Reporte actualizado exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@reporte_bp.route("/<reporte_id>", methods=["DELETE"])
def eliminar_reporte(reporte_id):
    """Eliminar un reporte"""
    try:
        reporte = Reporte.objects(reporte_id=reporte_id).first()
        if not reporte:
            return jsonify({"error": "Reporte no encontrado"}), 404
        
        reporte.delete()
        return jsonify({"msg": "Reporte eliminado exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@reporte_bp.route("/intento/<intento_id>", methods=["GET"])
def obtener_reporte_por_intento(intento_id):
    """Obtener reporte por ID de intento"""
    try:
        reporte = Reporte.objects(intento_id=intento_id).first()
        if not reporte:
            return jsonify({"error": "Reporte no encontrado para este intento"}), 404
        return jsonify(reporte.to_mongo().to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@reporte_bp.route("/<reporte_id>/retroalimentacion", methods=["PUT"])
def agregar_retroalimentacion_docente(reporte_id):
    """Agregar retroalimentación del docente al reporte"""
    try:
        data = request.json
        reporte = Reporte.objects(reporte_id=reporte_id).first()
        if not reporte:
            return jsonify({"error": "Reporte no encontrado"}), 404
        
        reporte.update(retroalimentacion_docente=data.get('retroalimentacion_docente'))
        return jsonify({"msg": "Retroalimentación agregada exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@reporte_bp.route("/<reporte_id>/ia", methods=["PUT"])
def actualizar_diagnostico_ia(reporte_id):
    """Actualizar diagnóstico y recomendaciones de IA"""
    try:
        data = request.json
        reporte = Reporte.objects(reporte_id=reporte_id).first()
        if not reporte:
            return jsonify({"error": "Reporte no encontrado"}), 404
        
        update_data = {}
        if 'diagnostico_ia' in data:
            update_data['diagnostico_ia'] = data['diagnostico_ia']
        if 'recomendaciones_ia' in data:
            update_data['recomendaciones_ia'] = data['recomendaciones_ia']
        
        reporte.update(**update_data)
        return jsonify({"msg": "Diagnóstico de IA actualizado exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400