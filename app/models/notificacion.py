from app import db
from datetime import datetime
from bson import ObjectId

class Notificacion:
    def __init__(self, notificacion_id, usuario_id, mensaje, tipo, estado="no leído"):
        self.notificacion_id = notificacion_id
        self.usuario_id = usuario_id
        self.mensaje = mensaje
        self.fecha = datetime.utcnow()
        self.tipo = tipo  # "alerta", "aviso", "recordatorio"
        self.estado = estado

    def save(self):
        """Guardar notificación en MongoDB"""
        if db is None:
            raise Exception("No hay conexión a la base de datos")

        notificacion_data = {
            "notificacion_id": self.notificacion_id,
            "usuario_id": self.usuario_id,
            "mensaje": self.mensaje,
            "fecha": self.fecha,
            "tipo": self.tipo,
            "estado": self.estado
        }

        result = db.notificaciones.insert_one(notificacion_data)
        self._id = result.inserted_id
        return result

    @staticmethod
    def find_all():
        """Obtener todas las notificaciones"""
        if db is None:
            return []
        return list(db.notificaciones.find())

    @staticmethod
    def find_by_id(notificacion_id):
        """Buscar notificación por ID"""
        if db is None:
            return None
        return db.notificaciones.find_one({"notificacion_id": notificacion_id})

    @staticmethod
    def find_by_usuario(usuario_id):
        """Buscar notificaciones por usuario"""
        if db is None:
            return []
        return list(db.notificaciones.find({"usuario_id": usuario_id}))

    @staticmethod
    def update_by_id(notificacion_id, update_data):
        """Actualizar notificación por ID"""
        if db is None:
            return None
        return db.notificaciones.update_one(
            {"notificacion_id": notificacion_id},
            {"$set": update_data}
        )

    @staticmethod
    def delete_by_id(notificacion_id):
        """Eliminar notificación por ID"""
        if db is None:
            return None
        return db.notificaciones.delete_one({"notificacion_id": notificacion_id})

    def to_json(self):
        """Convertir a diccionario para JSON"""
        return {
            "notificacion_id": self.notificacion_id,
            "usuario_id": self.usuario_id,
            "mensaje": self.mensaje,
            "fecha": self.fecha.isoformat(),
            "tipo": self.tipo,
            "estado": self.estado
        }
