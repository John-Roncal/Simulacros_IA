from app import db
from datetime import datetime
from bson import ObjectId

class Respuesta:
    def __init__(self, pregunta_id, opcion_marcada, es_correcta=False, feedback=""):
        self.pregunta_id = pregunta_id
        self.opcion_marcada = opcion_marcada
        self.es_correcta = es_correcta
        self.feedback = feedback
    
    def to_dict(self):
        return {
            "pregunta_id": self.pregunta_id,
            "opcion_marcada": self.opcion_marcada,
            "es_correcta": self.es_correcta,
            "feedback": self.feedback
        }

class Intento:
    def __init__(self, intento_id, evaluacion_id, alumno_id, fecha_inicio=None, 
                 fecha_fin=None, calificacion=None, estado="en progreso", respuestas=None,
                 feedback_alumno="", feedback_docente=""):
        self.intento_id = intento_id
        self.evaluacion_id = evaluacion_id
        self.alumno_id = alumno_id
        self.fecha_inicio = fecha_inicio or datetime.utcnow()
        self.fecha_fin = fecha_fin
        self.calificacion = calificacion
        self.estado = estado
        self.respuestas = respuestas or []
        self.feedback_alumno = feedback_alumno
        self.feedback_docente = feedback_docente
    
    def save(self):
        """Guardar intento en MongoDB"""
        if db is None:
            raise Exception("No hay conexión a la base de datos")
            
        intento_data = {
            "intento_id": self.intento_id,
            "evaluacion_id": self.evaluacion_id,
            "alumno_id": self.alumno_id,
            "fecha_inicio": self.fecha_inicio,
            "fecha_fin": self.fecha_fin,
            "calificacion": self.calificacion,
            "estado": self.estado,
            "respuestas": [r.to_dict() if isinstance(r, Respuesta) else r for r in self.respuestas],
            "feedback_alumno": self.feedback_alumno,
            "feedback_docente": self.feedback_docente
        }
        
        result = db.intentos.insert_one(intento_data)
        self._id = result.inserted_id
        return result
    
    @staticmethod
    def find_all():
        """Obtener todos los intentos"""
        if db is None:
            return []
        return list(db.intentos.find())
    
    @staticmethod
    def find_by_id(intento_id):
        """Buscar intento por ID"""
        if db is None:
            return None
        return db.intentos.find_one({"intento_id": intento_id})
    
    @staticmethod
    def find_by_alumno(alumno_id):
        """Buscar intentos por alumno"""
        if db is None:
            return []
        return list(db.intentos.find({"alumno_id": alumno_id}))
    
    @staticmethod
    def find_by_evaluacion(evaluacion_id):
        """Buscar intentos por evaluación"""
        if db is None:
            return []
        return list(db.intentos.find({"evaluacion_id": evaluacion_id}))
    
    @staticmethod
    def update_by_id(intento_id, update_data):
        """Actualizar intento por ID"""
        if db is None:
            return None
        return db.intentos.update_one(
            {"intento_id": intento_id}, 
            {"$set": update_data}
        )
    
    @staticmethod
    def delete_by_id(intento_id):
        """Eliminar intento por ID"""
        if db is None:
            return None
        return db.intentos.delete_one({"intento_id": intento_id})
    
    def to_json(self):
        """Convertir a diccionario para JSON"""
        return {
            "intento_id": self.intento_id,
            "evaluacion_id": self.evaluacion_id,
            "alumno_id": self.alumno_id,
            "fecha_inicio": self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            "fecha_fin": self.fecha_fin.isoformat() if self.fecha_fin else None,
            "calificacion": self.calificacion,
            "estado": self.estado,
            "respuestas": [r.to_dict() if isinstance(r, Respuesta) else r for r in self.respuestas],
            "feedback_alumno": self.feedback_alumno,
            "feedback_docente": self.feedback_docente
        }