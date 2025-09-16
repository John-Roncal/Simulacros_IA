import app
from datetime import datetime
from bson import ObjectId

class Usuario:
    def __init__(self, usuario_id, nombre, apellido, correo, contraseña_hash, rol, grado=None, seccion=None, estado="activo"):
        self.usuario_id = usuario_id
        self.nombre = nombre
        self.apellido = apellido
        self.correo = correo
        self.contraseña_hash = contraseña_hash
        self.rol = rol  # "Alumno", "Docente", "Admin"
        self.grado = grado
        self.seccion = seccion
        self.estado = estado
        self.fecha_creacion = datetime.utcnow()
    
    def save(self):
        """Guardar usuario en MongoDB"""
        usuario_data = {
            "usuario_id": self.usuario_id,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "correo": self.correo,
            "contraseña_hash": self.contraseña_hash,
            "rol": self.rol,
            "grado": self.grado,
            "seccion": self.seccion,
            "estado": self.estado,
            "fecha_creacion": self.fecha_creacion
        }
        
        result = app.db.usuarios.insert_one(usuario_data)
        self._id = result.inserted_id
        return result
    
    @staticmethod
    def find_all():
        """Obtener todos los usuarios"""
        return list(app.db.usuarios.find())
    
    @staticmethod
    def find_by_id(usuario_id):
        """Buscar usuario por ID"""
        return app.db.usuarios.find_one({"usuario_id": usuario_id})
    
    @staticmethod
    def find_by_email(correo):
        """Buscar usuario por email"""
        return app.db.usuarios.find_one({"correo": correo})
    
    @staticmethod
    def update_by_id(usuario_id, update_data):
        """Actualizar usuario por ID"""
        return app.db.usuarios.update_one(
            {"usuario_id": usuario_id}, 
            {"$set": update_data}
        )
    
    @staticmethod
    def delete_by_id(usuario_id):
        """Eliminar usuario por ID"""
        return app.db.usuarios.delete_one({"usuario_id": usuario_id})
    
    def to_json(self):
        """Convertir a diccionario para JSON"""
        return {
            "usuario_id": self.usuario_id,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "correo": self.correo,
            "rol": self.rol,
            "grado": self.grado,
            "seccion": self.seccion,
            "estado": self.estado,
            "fecha_creacion": self.fecha_creacion.isoformat()
        }