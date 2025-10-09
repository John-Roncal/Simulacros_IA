from bson.objectid import ObjectId

class Seccion:
    def __init__(self, nombre, grado_id, estado, _id=None):
        self.nombre = nombre
        self.grado_id = grado_id
        self.estado = estado
        self._id = _id if _id else ObjectId()

    def to_dict(self):
        return {
            "_id": str(self._id),
            "nombre": self.nombre,
            "grado_id": self.grado_id,
            "estado": self.estado
        }

    @staticmethod
    def from_dict(data):
        return Seccion(
            nombre=data.get('nombre'),
            grado_id=data.get('grado_id'),
            estado=data.get('estado', True),
            _id=ObjectId(data.get('_id')) if data.get('_id') else None
        )