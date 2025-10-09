from bson.objectid import ObjectId

class Grado:
    def __init__(self, nombre, descripcion, estado, _id=None):
        self.nombre = nombre
        self.descripcion = descripcion
        self.estado = estado
        self._id = _id if _id else ObjectId()

    def to_dict(self):
        return {
            "_id": str(self._id),
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "estado": self.estado
        }

    @staticmethod
    def from_dict(data):
        return Grado(
            nombre=data.get('nombre'),
            descripcion=data.get('descripcion'),
            estado=data.get('estado', True),
            _id=ObjectId(data.get('_id')) if data.get('_id') else None
        )