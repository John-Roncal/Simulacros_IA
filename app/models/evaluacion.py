from app import db
from datetime import datetime
from bson import ObjectId

class Pregunta:
    def __init__(self, pregunta_id, tipo, enunciado, opciones, respuesta_correcta):
        self.pregunta_id = pregunta_id
        self.tipo = tipo  # "OM" o "VF"
        self.enunciado = enunciado
        self.opciones = opciones  # Lista de strings
        self.respuesta_correcta = respuesta_correcta
    
    def to_dict(self):
        return {
            "pregunta_id": self.pregunta_id,
            "tipo": self.tipo,
            "enunciado": self.enunciado,
            "opciones": self.opciones,
            "respuesta_correcta": self.respuesta_correcta
        }

class Evaluacion:
    def __init__(self, evaluacion_id, titulo, materia, grado, seccion, docente_id, 
                 fecha_entrega, intentos_permitidos=1, estado="activa", preguntas=None):
        self.evaluacion_id = evaluacion_id
        self.titulo = titulo
        self.materia = materia
        self.grado = grado
        self.seccion = seccion
        self.docente_id = docente_id
        self.fecha_creacion = datetime.utcnow()
        self.fecha_entrega = fecha_entrega
        self.estado = estado
        self.intentos_permitidos = intentos_permitidos
        self.preguntas = preguntas or []
    
    def save(self):
        """Guardar evaluación en MongoDB"""
        if db is None:
            raise Exception("No hay conexión a la base de datos")
            
        evaluacion_data = {
            "evaluacion_id": self.evaluacion_id,
            "titulo": self.titulo,
            "materia": self.materia,
            "grado": self.grado,
            "seccion": self.seccion,
            "docente_id": self.docente_id,
            "fecha_creacion": self.fecha_creacion,
            "fecha_entrega": self.fecha_entrega,
            "estado": self.estado,
            "intentos_permitidos": self.intentos_permitidos,
            "preguntas": [p.to_dict() if isinstance(p, Pregunta) else p for p in self.preguntas]
        }
        
        result = db.evaluaciones.insert_one(evaluacion_data)
        self._id = result.inserted_id
        return result
    
    @staticmethod
    def find_all():
        """Obtener todas las evaluaciones"""
        if db is None:
            return []
        return list(db.evaluaciones.find())
    
    @staticmethod
    def find_by_id(evaluacion_id):
        """Buscar evaluación por ID"""
        if db is None:
            return None
        return db.evaluaciones.find_one({"evaluacion_id": evaluacion_id})
    
    @staticmethod
    def find_by_docente(docente_id):
        """Buscar evaluaciones por docente"""
        if db is None:
            return []
        return list(db.evaluaciones.find({"docente_id": docente_id}))
    
    @staticmethod
    def find_by_filters(filters):
        """Buscar evaluaciones por filtros"""
        if db is None:
            return []
        return list(db.evaluaciones.find(filters))
    
    @staticmethod
    def update_by_id(evaluacion_id, update_data):
        """Actualizar evaluación por ID"""
        if db is None:
            return None
        return db.evaluaciones.update_one(
            {"evaluacion_id": evaluacion_id}, 
            {"$set": update_data}
        )
    
    @staticmethod
    def delete_by_id(evaluacion_id):
        """Eliminar evaluación por ID"""
        if db is None:
            return None
        return db.evaluaciones.delete_one({"evaluacion_id": evaluacion_id})
    
    def to_json(self):
        """Convertir a diccionario para JSON"""
        return {
            "evaluacion_id": self.evaluacion_id,
            "titulo": self.titulo,
            "materia": self.materia,
            "grado": self.grado,
            "seccion": self.seccion,
            "docente_id": self.docente_id,
            "fecha_creacion": self.fecha_creacion.isoformat(),
            "fecha_entrega": self.fecha_entrega.isoformat() if self.fecha_entrega else None,
            "estado": self.estado,
            "intentos_permitidos": self.intentos_permitidos,
            "preguntas": [p.to_dict() if isinstance(p, Pregunta) else p for p in self.preguntas]
        }