from flask import Blueprint, request, jsonify, make_response
from app.models.reporte import Reporte
from app.models.intento import Intento
from app.models.evaluacion import Evaluacion
from app.models.usuario import Usuario
from datetime import datetime, timedelta
import uuid
from fpdf import FPDF
import io

reporte_bp = Blueprint("reportes", __name__)

@reporte_bp.route("", methods=["POST"])
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

@reporte_bp.route("/semanal/alumno/<string:alumno_id>", methods=["GET"])
def generar_reporte_semanal_alumno(alumno_id):
    """Genera y devuelve un reporte semanal de notas para un alumno en formato PDF."""
    try:
        # Validar que el alumno exista
        alumno = Usuario.find_by_id(alumno_id)
        if not alumno or alumno.rol != "Alumno":
            return jsonify({"error": "Alumno no encontrado"}), 404

        # Obtener la fecha de inicio y fin de la última semana
        fecha_fin = datetime.utcnow()
        fecha_inicio = fecha_fin - timedelta(days=7)

        # Buscar todos los intentos del alumno en la última semana
        intentos = Intento.find_by_alumno_in_date_range(alumno_id, fecha_inicio, fecha_fin)

        if not intentos:
            return jsonify({"error": "No se encontraron intentos para este alumno en la última semana"}), 404

        # Procesar los datos para el reporte
        notas_por_materia = {}
        for intento in intentos:
            evaluacion = Evaluacion.find_by_id(intento["evaluacion_id"])
            if evaluacion:
                materia = evaluacion["materia"]
                calificacion = intento["calificacion"]
                if materia not in notas_por_materia:
                    notas_por_materia[materia] = []
                notas_por_materia[materia].append(calificacion)

        # Calcular promedios
        promedios_por_materia = {materia: sum(notas) / len(notas) for materia, notas in notas_por_materia.items()}

        # Generar el PDF
        pdf_buffer = generar_pdf_reporte(alumno, promedios_por_materia, fecha_inicio, fecha_fin)

        # Devolver el PDF como respuesta
        response = make_response(pdf_buffer.getvalue())
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = f"attachment; filename=reporte_semanal_{alumno_id}.pdf"
        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def generar_pdf_reporte(alumno, promedios, fecha_inicio, fecha_fin):
    """Genera un reporte en PDF y lo devuelve como un buffer de bytes."""
    pdf = FPDF()
    pdf.add_page()

    # Título
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Reporte Semanal de Calificaciones", 0, 1, "C")
    pdf.ln(10)

    # Información del alumno
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Alumno: {alumno.nombre} {alumno.apellido}", 0, 1)
    pdf.cell(0, 10, f"Semana del {fecha_inicio.strftime('%d/%m/%Y')} al {fecha_fin.strftime('%d/%m/%Y')}", 0, 1)
    pdf.ln(10)

    # Tabla de promedios
    pdf.set_font("Arial", "B", 12)
    pdf.cell(100, 10, "Materia", 1)
    pdf.cell(50, 10, "Promedio", 1)
    pdf.ln()

    pdf.set_font("Arial", "", 12)
    for materia, promedio in promedios.items():
        pdf.cell(100, 10, materia, 1)
        pdf.cell(50, 10, f"{promedio:.2f}", 1)
        pdf.ln()

    # Convertir a buffer de bytes
    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer