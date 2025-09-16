from app import db
from datetime import datetime
from bson import ObjectId

class Reporte:
    def __init__(self, reporte_id, intento_id, diagnostico_ia=None, 
                 recomendaciones_ia=None, retroalimentacion_docente=None):
        self.reporte_id = reporte_id
        self.intento_id = intento_id
        self.diagnostico_ia = diagnostico_ia
        self.recomendaciones_ia = recomendaciones_ia
        self.retroalimentacion_docente = retroalimentacion_docente
        self.fecha_creacion = datetime.utcnow()
    
    def save(self):
        """Guardar reporte en MongoDB"""
        if not db:
            raise Exception("No hay conexión a la base de datos")
            
        reporte_data = {
            "reporte_id": self.reporte_id,
            "intento_id": self.intento_id,
            "diagnostico_ia": self.diagnostico_ia,
            "recomendaciones_ia": self.recomendaciones_ia,
            "retroalimentacion_docente": self.retroalimentacion_docente,
            "fecha_creacion": self.fecha_creacion
        }
        
        result = db.reportes.insert_one(reporte_data)
        self._id = result.inserted_id
        return result
    
    @staticmethod
    def find_all():
        """Obtener todos los reportes"""
        if not db:
            return []
        return list(db.reportes.find())
    
    @staticmethod
    def find_by_id(reporte_id):
        """Buscar reporte por ID"""
        if not db:
            return None
        return db.reportes.find_one({"reporte_id": reporte_id})
    
    @staticmethod
    def find_by_intento(intento_id):
        """Buscar reporte por intento"""
        if not db:
            return None
        return db.reportes.find_one({"intento_id": intento_id})
    
    @staticmethod
    def update_by_id(reporte_id, update_data):
        """Actualizar reporte por ID"""
        if not db:
            return None
        return db.reportes.update_one(
            {"reporte_id": reporte_id}, 
            {"$set": update_data}
        )
    
    @staticmethod
    def delete_by_id(reporte_id):
        """Eliminar reporte por ID"""
        if not db:
            return None
        return db.reportes.delete_one({"reporte_id": reporte_id})
    
    def to_json(self):
        """Convertir a diccionario para JSON"""
        return {
            "reporte_id": self.reporte_id,
            "intento_id": self.intento_id,
            "diagnostico_ia": self.diagnostico_ia,
            "recomendaciones_ia": self.recomendaciones_ia,
            "retroalimentacion_docente": self.retroalimentacion_docente,
            "fecha_creacion": self.fecha_creacion.isoformat()
        }