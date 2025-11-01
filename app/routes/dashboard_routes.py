from flask import Blueprint, request, jsonify
from app.models.usuario import Usuario
from app.models.evaluacion import Evaluacion
from app.models.intento import Intento
from collections import defaultdict
from datetime import datetime

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/summary", methods=["GET"])
def get_summary():
    """
    Obtiene estadísticas generales del sistema.
    
    Returns:
        {
            "total_alumnos": int,
            "total_docentes": int,
            "total_salones_activos": int,
            "total_evaluaciones": int,
            "total_intentos": int
        }
    """
    try:
        total_alumnos = len(Usuario.find_by_role("Alumno"))
        total_docentes = len(Usuario.find_by_role("Docente"))

        # Calcular salones activos únicos (grado + sección)
        alumnos = Usuario.find_by_role("Alumno")
        salones_activos = set()
        
        for alumno in alumnos:
            grado = _extract_value(alumno.grado)
            seccion = _extract_value(alumno.seccion)
            
            if grado and seccion:
                salones_activos.add((str(grado), str(seccion)))

        # Estadísticas adicionales
        total_evaluaciones = len(Evaluacion.find_all())
        total_intentos = len(Intento.find_all())

        return jsonify({
            "total_alumnos": total_alumnos,
            "total_docentes": total_docentes,
            "total_salones_activos": len(salones_activos),
            "total_evaluaciones": total_evaluaciones,
            "total_intentos": total_intentos
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route("/performance/classroom", methods=["GET"])
def get_classroom_performance():
    """
    Obtiene el rendimiento académico de un salón específico.
    
    Query Params:
        - grado (required): Grado del salón (ej: "3°")
        - seccion (required): Sección del salón (ej: "A")
        - fecha_inicio (optional): Fecha inicio en formato YYYY-MM-DD
        - fecha_fin (optional): Fecha fin en formato YYYY-MM-DD
    
    Returns:
        {
            "salon": "3° A",
            "data": [
                {
                    "fecha": "2025-01-15",
                    "promedio": 15.5,
                    "total_intentos": 25,
                    "total_alumnos": 25
                }
            ]
        }
    """
    try:
        grado = request.args.get("grado")
        seccion = request.args.get("seccion")
        
        if not grado or not seccion:
            return jsonify({"error": "Se requieren los parámetros 'grado' y 'seccion'"}), 400

        # Filtros de fecha opcionales
        fecha_inicio = request.args.get("fecha_inicio")
        fecha_fin = request.args.get("fecha_fin")

        # Buscar evaluaciones del salón específico
        evaluaciones = Evaluacion.find_by_filters({
            "grado": grado,
            "seccion": seccion
        })

        if not evaluaciones:
            return jsonify({
                "salon": f"{grado} {seccion}",
                "data": [],
                "mensaje": "No se encontraron evaluaciones para este salón"
            }), 200

        # Obtener todos los intentos finalizados de esas evaluaciones
        evaluacion_ids = [ev["evaluacion_id"] for ev in evaluaciones]
        
        # Agrupar calificaciones por fecha
        calificaciones_por_fecha = defaultdict(list)
        
        for eval_id in evaluacion_ids:
            intentos = Intento.find_by_evaluacion(eval_id)
            
            for intento in intentos:
                # Solo intentos finalizados con calificación
                if intento.get("estado") == "finalizado" and intento.get("calificacion") is not None:
                    fecha_fin_intento = intento.get("fecha_fin")
                    
                    if fecha_fin_intento:
                        fecha_str = fecha_fin_intento.strftime('%Y-%m-%d')
                        
                        # Aplicar filtros de fecha si existen
                        if fecha_inicio and fecha_str < fecha_inicio:
                            continue
                        if fecha_fin and fecha_str > fecha_fin:
                            continue
                        
                        calificaciones_por_fecha[fecha_str].append(intento["calificacion"])

        # Calcular promedios por fecha
        data = []
        for fecha, calificaciones in sorted(calificaciones_por_fecha.items()):
            promedio = sum(calificaciones) / len(calificaciones)
            data.append({
                "fecha": fecha,
                "promedio": round(promedio, 2),
                "total_intentos": len(calificaciones),
                "calificacion_maxima": max(calificaciones),
                "calificacion_minima": min(calificaciones)
            })

        return jsonify({
            "salon": f"{grado} {seccion}",
            "total_evaluaciones": len(evaluaciones),
            "data": data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route("/performance/student/<int:alumno_id>", methods=["GET"])
def get_student_performance(alumno_id):
    """
    Obtiene el rendimiento académico de un alumno específico.
    
    Path Params:
        - alumno_id: ID del alumno
    
    Query Params:
        - fecha_inicio (optional): Fecha inicio en formato YYYY-MM-DD
        - fecha_fin (optional): Fecha fin en formato YYYY-MM-DD
        - materia (optional): Filtrar por materia específica
    
    Returns:
        {
            "alumno": {
                "usuario_id": 5,
                "nombre": "Juan Pérez",
                "grado": "3°",
                "seccion": "A"
            },
            "estadisticas": {
                "promedio_general": 15.8,
                "total_evaluaciones": 10,
                "evaluaciones_aprobadas": 8,
                "evaluaciones_reprobadas": 2
            },
            "data": [
                {
                    "fecha": "2025-01-15",
                    "calificacion": 16,
                    "evaluacion_titulo": "Matemática - Álgebra",
                    "materia": "Matemática"
                }
            ]
        }
    """
    try:
        # Verificar que el alumno existe
        alumno = Usuario.find_by_id(alumno_id)
        if not alumno or alumno.rol != "Alumno":
            return jsonify({"error": "Alumno no encontrado"}), 404

        # Filtros opcionales
        fecha_inicio = request.args.get("fecha_inicio")
        fecha_fin = request.args.get("fecha_fin")
        materia = request.args.get("materia")

        # Obtener todos los intentos del alumno
        intentos = Intento.find_by_alumno(str(alumno_id))
        
        # Crear mapa de evaluaciones para obtener información adicional
        evaluaciones_map = {}
        for intento in intentos:
            eval_id = intento.get("evaluacion_id")
            if eval_id and eval_id not in evaluaciones_map:
                evaluacion = Evaluacion.find_by_id(eval_id)
                if evaluacion:
                    evaluaciones_map[eval_id] = evaluacion

        # Procesar datos
        data = []
        calificaciones = []
        aprobadas = 0
        reprobadas = 0

        for intento in intentos:
            # Solo intentos finalizados
            if intento.get("estado") != "finalizado" or intento.get("calificacion") is None:
                continue

            fecha_fin_intento = intento.get("fecha_fin")
            if not fecha_fin_intento:
                continue

            fecha_str = fecha_fin_intento.strftime('%Y-%m-%d')
            
            # Aplicar filtros de fecha
            if fecha_inicio and fecha_str < fecha_inicio:
                continue
            if fecha_fin and fecha_str > fecha_fin:
                continue

            # Obtener información de la evaluación
            eval_id = intento.get("evaluacion_id")
            evaluacion = evaluaciones_map.get(eval_id, {})
            
            materia_eval = evaluacion.get("materia", "Sin materia")
            
            # Aplicar filtro de materia
            if materia and materia_eval.lower() != materia.lower():
                continue

            calificacion = intento["calificacion"]
            calificaciones.append(calificacion)
            
            # Contar aprobados/reprobados (nota mínima 11 en Perú)
            if calificacion >= 11:
                aprobadas += 1
            else:
                reprobadas += 1

            data.append({
                "fecha": fecha_str,
                "calificacion": calificacion,
                "evaluacion_titulo": evaluacion.get("titulo", "Sin título"),
                "materia": materia_eval,
                "evaluacion_id": eval_id,
                "intento_id": intento.get("intento_id")
            })

        # Ordenar por fecha ascendente
        data.sort(key=lambda x: x["fecha"])

        # Calcular estadísticas
        promedio = sum(calificaciones) / len(calificaciones) if calificaciones else 0

        return jsonify({
            "alumno": {
                "usuario_id": alumno.usuario_id,
                "nombre": f"{alumno.nombre} {alumno.apellido}",
                "grado": _extract_value(alumno.grado),
                "seccion": _extract_value(alumno.seccion)
            },
            "estadisticas": {
                "promedio_general": round(promedio, 2),
                "total_evaluaciones": len(calificaciones),
                "evaluaciones_aprobadas": aprobadas,
                "evaluaciones_reprobadas": reprobadas,
                "tasa_aprobacion": round((aprobadas / len(calificaciones) * 100), 2) if calificaciones else 0
            },
            "data": data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route("/performance/comparison", methods=["GET"])
def get_performance_comparison():
    """
    Compara el rendimiento entre múltiples alumnos.
    
    Query Params:
        - alumno_ids (required): IDs de alumnos separados por coma (ej: "1,2,3")
        - materia (optional): Filtrar por materia
    
    Returns:
        {
            "alumnos": [
                {
                    "alumno_id": 1,
                    "nombre": "Juan Pérez",
                    "promedio": 15.5,
                    "total_evaluaciones": 10
                }
            ]
        }
    """
    try:
        alumno_ids_str = request.args.get("alumno_ids")
        if not alumno_ids_str:
            return jsonify({"error": "Se requiere el parámetro 'alumno_ids'"}), 400

        materia = request.args.get("materia")
        alumno_ids = [int(id.strip()) for id in alumno_ids_str.split(",")]

        resultados = []
        
        for alumno_id in alumno_ids:
            alumno = Usuario.find_by_id(alumno_id)
            if not alumno or alumno.rol != "Alumno":
                continue

            intentos = Intento.find_by_alumno(str(alumno_id))
            calificaciones = []

            for intento in intentos:
                if intento.get("estado") == "finalizado" and intento.get("calificacion") is not None:
                    # Filtrar por materia si es necesario
                    if materia:
                        eval_id = intento.get("evaluacion_id")
                        evaluacion = Evaluacion.find_by_id(eval_id)
                        if not evaluacion or evaluacion.get("materia", "").lower() != materia.lower():
                            continue
                    
                    calificaciones.append(intento["calificacion"])

            promedio = sum(calificaciones) / len(calificaciones) if calificaciones else 0

            resultados.append({
                "alumno_id": alumno.usuario_id,
                "nombre": f"{alumno.nombre} {alumno.apellido}",
                "promedio": round(promedio, 2),
                "total_evaluaciones": len(calificaciones)
            })

        # Ordenar por promedio descendente
        resultados.sort(key=lambda x: x["promedio"], reverse=True)

        return jsonify({"alumnos": resultados}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route("/performance/by-subject", methods=["GET"])
def get_performance_by_subject():
    """
    Obtiene el rendimiento promedio por materia en un salón.
    
    Query Params:
        - grado (required): Grado del salón
        - seccion (required): Sección del salón
    
    Returns:
        {
            "salon": "3° A",
            "materias": [
                {
                    "materia": "Matemática",
                    "promedio": 14.5,
                    "total_evaluaciones": 5,
                    "total_intentos": 125
                }
            ]
        }
    """
    try:
        grado = request.args.get("grado")
        seccion = request.args.get("seccion")
        
        if not grado or not seccion:
            return jsonify({"error": "Se requieren los parámetros 'grado' y 'seccion'"}), 400

        # Buscar evaluaciones del salón
        evaluaciones = Evaluacion.find_by_filters({
            "grado": grado,
            "seccion": seccion
        })

        # Agrupar por materia
        materias_data = defaultdict(lambda: {"calificaciones": [], "total_evaluaciones": 0})
        
        for evaluacion in evaluaciones:
            materia = evaluacion.get("materia", "Sin materia")
            materias_data[materia]["total_evaluaciones"] += 1
            
            # Obtener intentos de esta evaluación
            intentos = Intento.find_by_evaluacion(evaluacion["evaluacion_id"])
            
            for intento in intentos:
                if intento.get("estado") == "finalizado" and intento.get("calificacion") is not None:
                    materias_data[materia]["calificaciones"].append(intento["calificacion"])

        # Calcular promedios
        resultados = []
        for materia, data in materias_data.items():
            calificaciones = data["calificaciones"]
            promedio = sum(calificaciones) / len(calificaciones) if calificaciones else 0
            
            resultados.append({
                "materia": materia,
                "promedio": round(promedio, 2),
                "total_evaluaciones": data["total_evaluaciones"],
                "total_intentos": len(calificaciones)
            })

        # Ordenar por promedio descendente
        resultados.sort(key=lambda x: x["promedio"], reverse=True)

        return jsonify({
            "salon": f"{grado} {seccion}",
            "materias": resultados
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route("/top-students", methods=["GET"])
def get_top_students():
    """
    Obtiene el ranking de mejores estudiantes.
    
    Query Params:
        - grado (optional): Filtrar por grado
        - seccion (optional): Filtrar por sección
        - limit (optional): Número de estudiantes a retornar (default: 10)
    
    Returns:
        {
            "ranking": [
                {
                    "posicion": 1,
                    "alumno_id": 5,
                    "nombre": "María García",
                    "promedio": 18.5,
                    "total_evaluaciones": 12
                }
            ]
        }
    """
    try:
        grado = request.args.get("grado")
        seccion = request.args.get("seccion")
        limit = int(request.args.get("limit", 10))

        # Obtener alumnos
        filtros = {"rol": "Alumno", "estado": "activo"}
        alumnos = Usuario.find_by_role("Alumno")

        # Filtrar por grado/sección si se proporciona
        if grado or seccion:
            alumnos_filtrados = []
            for alumno in alumnos:
                grado_alumno = _extract_value(alumno.grado)
                seccion_alumno = _extract_value(alumno.seccion)
                
                if grado and str(grado_alumno) != str(grado):
                    continue
                if seccion and str(seccion_alumno) != str(seccion):
                    continue
                
                alumnos_filtrados.append(alumno)
            alumnos = alumnos_filtrados

        # Calcular promedios
        ranking = []
        for alumno in alumnos:
            intentos = Intento.find_by_alumno(str(alumno.usuario_id))
            calificaciones = [
                i["calificacion"] for i in intentos 
                if i.get("estado") == "finalizado" and i.get("calificacion") is not None
            ]

            if calificaciones:  # Solo incluir alumnos con evaluaciones
                promedio = sum(calificaciones) / len(calificaciones)
                ranking.append({
                    "alumno_id": alumno.usuario_id,
                    "nombre": f"{alumno.nombre} {alumno.apellido}",
                    "grado": _extract_value(alumno.grado),
                    "seccion": _extract_value(alumno.seccion),
                    "promedio": round(promedio, 2),
                    "total_evaluaciones": len(calificaciones)
                })

        # Ordenar por promedio descendente
        ranking.sort(key=lambda x: x["promedio"], reverse=True)

        # Agregar posición
        for idx, estudiante in enumerate(ranking[:limit], 1):
            estudiante["posicion"] = idx

        return jsonify({"ranking": ranking[:limit]}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route("/activity-timeline", methods=["GET"])
def get_activity_timeline():
    """
    Obtiene una línea de tiempo de actividad reciente.
    
    Query Params:
        - limit (optional): Número de actividades (default: 20)
    
    Returns:
        {
            "actividades": [
                {
                    "fecha": "2025-01-15T10:30:00",
                    "tipo": "intento_finalizado",
                    "descripcion": "Juan Pérez finalizó la evaluación de Matemática",
                    "datos": {...}
                }
            ]
        }
    """
    try:
        limit = int(request.args.get("limit", 20))

        # Obtener intentos recientes
        intentos = sorted(
            Intento.find_all(),
            key=lambda x: x.get("fecha_inicio", datetime.min),
            reverse=True
        )[:limit]

        actividades = []
        for intento in intentos:
            alumno = Usuario.find_by_id(int(intento.get("alumno_id", 0)))
            evaluacion = Evaluacion.find_by_id(intento.get("evaluacion_id"))

            if alumno and evaluacion:
                estado = intento.get("estado")
                fecha = intento.get("fecha_fin" if estado == "finalizado" else "fecha_inicio")

                descripcion = f"{alumno.nombre} {alumno.apellido} "
                if estado == "finalizado":
                    descripcion += f"finalizó la evaluación '{evaluacion.get('titulo')}' con nota {intento.get('calificacion', 0)}"
                else:
                    descripcion += f"inició la evaluación '{evaluacion.get('titulo')}'"

                actividades.append({
                    "fecha": fecha.isoformat() if fecha else None,
                    "tipo": f"intento_{estado}",
                    "descripcion": descripcion,
                    "datos": {
                        "alumno_id": alumno.usuario_id,
                        "alumno_nombre": f"{alumno.nombre} {alumno.apellido}",
                        "evaluacion_id": evaluacion.get("evaluacion_id"),
                        "evaluacion_titulo": evaluacion.get("titulo"),
                        "calificacion": intento.get("calificacion")
                    }
                })

        return jsonify({"actividades": actividades}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================
# FUNCIONES AUXILIARES
# ============================================

def _extract_value(field):
    """
    Extrae el valor de un campo que puede ser string, list o dict.
    Útil para manejar campos como grado y sección que pueden tener diferentes formatos.
    """
    if field is None:
        return None
    if isinstance(field, list):
        return field[0] if field else None
    if isinstance(field, dict):
        return field.get('nombre') or field.get('_id')
    return field