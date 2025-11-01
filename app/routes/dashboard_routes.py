from flask import Blueprint, jsonify
from app.models.usuario import Usuario
from app.models.evaluacion import Evaluacion
from app.models.intento import Intento

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/summary", methods=["GET"])
def get_summary():
    try:
        total_alumnos = len(Usuario.find_by_role("Alumno"))
        total_docentes = len(Usuario.find_by_role("Docente"))

        alumnos = Usuario.find_by_role("Alumno")
        salones_activos = set()
        for alumno in alumnos:
            if alumno.grado and alumno.seccion:
                salones_activos.add((alumno.grado, alumno.seccion))

        total_salones_activos = len(salones_activos)

        return jsonify({
            "total_alumnos": total_alumnos,
            "total_docentes": total_docentes,
            "total_salones_activos": total_salones_activos
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route("/performance/student", methods=["GET"])
def get_student_performance():
    try:
        intentos = Intento.find_all()
        alumnos = Usuario.find_by_role("Alumno")

        alumno_map = {alumno.usuario_id: f"{alumno.nombre} {alumno.apellido}" for alumno in alumnos}

        student_performance = {}

        for intento in intentos:
            alumno_id = intento.get("alumno_id")
            if alumno_id in alumno_map:
                student_name = alumno_map[alumno_id]

                if student_name not in student_performance:
                    student_performance[student_name] = []

                if "fecha_fin" in intento and "calificacion" in intento:
                    student_performance[student_name].append({
                        "date": intento["fecha_fin"].strftime('%Y-%m-%d'),
                        "grade": intento["calificacion"]
                    })

        # Sort by date for each student
        for student, grades in student_performance.items():
            student_performance[student] = sorted(grades, key=lambda x: x['date'])

        return jsonify(student_performance), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route("/performance/classroom", methods=["GET"])
def get_classroom_performance():
    try:
        intentos = Intento.find_all()
        evaluaciones = Evaluacion.find_all()

        evaluacion_map = {str(eval["_id"]): eval for eval in evaluaciones}

        classroom_performance = {}

        for intento in intentos:
            if "evaluacion_id" in intento and str(intento["evaluacion_id"]) in evaluacion_map:
                eval_info = evaluacion_map[str(intento["evaluacion_id"])]
                classroom_key = f"{eval_info['grado']}° \"{eval_info['seccion']}\""

                if classroom_key not in classroom_performance:
                    classroom_performance[classroom_key] = {}

                if "fecha_fin" in intento and "calificacion" in intento:
                    date_key = intento["fecha_fin"].strftime('%Y-%m-%d')
                    if date_key not in classroom_performance[classroom_key]:
                        classroom_performance[classroom_key][date_key] = []

                    classroom_performance[classroom_key][date_key].append(intento["calificacion"])

        # Calculate averages
        for classroom, dates in classroom_performance.items():
            for date, grades in dates.items():
                classroom_performance[classroom][date] = sum(grades) / len(grades) if grades else 0

        # Format for chart
        formatted_performance = {}
        for classroom, dates in classroom_performance.items():
            formatted_performance[classroom] = sorted(
                [{"date": date, "average_grade": avg} for date, avg in dates.items()],
                key=lambda x: x['date']
            )

        return jsonify(formatted_performance), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
