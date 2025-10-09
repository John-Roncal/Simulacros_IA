import app
from datetime import datetime, timezone
from bson import ObjectId
import bcrypt

class Usuario:
    def __init__(self, nombre, apellido, correo, contraseña_hash, rol, usuario_id=None, grado=None, seccion=None, estado="activo", _id=None, fecha_creacion=None):
        self._id = _id if _id else ObjectId()
        self.usuario_id = usuario_id
        self.nombre = nombre
        self.apellido = apellido
        self.correo = correo
        self.contraseña_hash = contraseña_hash
        self.rol = rol

        if rol == "Docente":
            self.grado = grado if isinstance(grado, list) else [grado]
            self.seccion = seccion if isinstance(seccion, list) else [seccion]
        else:
            self.grado = grado
            self.seccion = seccion

        self.estado = estado
        self.fecha_creacion = fecha_creacion or datetime.now(timezone.utc)

    def save(self):
        if self.usuario_id is None:
            self.usuario_id = self.get_next_user_id()

        usuario_data = self.to_dict()
        # The password hash is bytes, but we want to store it in a BSON-compatible way.
        # Pymongo handles bytes correctly, so we don't need to decode it.
        usuario_data['contraseña_hash'] = self.contraseña_hash

        # Remove id before insertion if it's new
        if '_id' in usuario_data and not self._id:
             del usuario_data['_id']

        result = app.db.usuarios.insert_one(self.to_dict())
        self._id = result.inserted_id
        return result

    def to_dict(self):
        return {
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

    @classmethod
    def from_mongo(cls, data):
        if not data:
            return None
        return cls(
            _id=data.get('_id'),
            usuario_id=data.get('usuario_id'),
            nombre=data.get('nombre'),
            apellido=data.get('apellido'),
            correo=data.get('correo'),
            contraseña_hash=data.get('contraseña_hash'),
            rol=data.get('rol'),
            grado=data.get('grado'),
            seccion=data.get('seccion'),
            estado=data.get('estado'),
            fecha_creacion=data.get('fecha_creacion')
        )

    @staticmethod
    def get_next_user_id():
        last_user = app.db.usuarios.find_one(
            {"usuario_id": {"$type": ["double", "int", "long"]}},
            sort=[("usuario_id", -1)]
        )
        if last_user and isinstance(last_user.get("usuario_id"), (int, float)):
            return int(last_user["usuario_id"]) + 1
        return 1

    @staticmethod
    def find_all():
        return [Usuario.from_mongo(user_data) for user_data in app.db.usuarios.find()]

    @staticmethod
    def find_by_id(usuario_id):
        user_data = app.db.usuarios.find_one({"usuario_id": usuario_id})
        return Usuario.from_mongo(user_data)

    @staticmethod
    def find_by_role(rol):
        return [Usuario.from_mongo(user_data) for user_data in app.db.usuarios.find({"rol": rol, "estado": "activo"})]
    
    @staticmethod
    def find_by_email(correo):
        user_data = app.db.usuarios.find_one({"correo": correo})
        return Usuario.from_mongo(user_data)
    
    @staticmethod
    def update_by_id(usuario_id, update_data):
        return app.db.usuarios.update_one(
            {"usuario_id": usuario_id}, 
            {"$set": update_data}
        )
    
    @staticmethod
    def delete_by_id(usuario_id):
        return app.db.usuarios.delete_one({"usuario_id": usuario_id})
    
    def to_json(self):
        data = self.to_dict()
        data['_id'] = str(self._id)
        data['fecha_creacion'] = self.fecha_creacion.isoformat()
        # Do not expose password hash
        del data['contraseña_hash']
        return data