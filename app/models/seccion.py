from bson.objectid import ObjectId

class Seccion:
    def __init__(self, nombre, grado_id, estado=True, _id=None):
        self.nombre = nombre
        self.grado_id = Seccion._ensure_objectid(grado_id)
        self.estado = estado
        self._id = _id if _id else ObjectId()

    def to_dict(self):
        """Dict para MongoDB (tipos nativos)."""
        return {
            "_id": self._id,
            "nombre": self.nombre,
            "grado_id": self.grado_id,
            "estado": self.estado
        }

    def to_json(self):
        """Dict serializable a JSON."""
        return {
            "_id": str(self._id),
            "nombre": self.nombre,
            "grado_id": str(self.grado_id) if self.grado_id else None,
            "estado": self.estado
        }

    @staticmethod
    def _ensure_objectid(value):
        if value is None:
            return None
        if isinstance(value, ObjectId):
            return value
        try:
            return ObjectId(value)
        except Exception:
            return None

    @staticmethod
    def from_dict(data):
        _id = Seccion._ensure_objectid(data.get('_id'))
        grado_id = Seccion._ensure_objectid(data.get('grado_id'))
        return Seccion(
            nombre=data.get('nombre'),
            grado_id=grado_id,
            estado=data.get('estado', True),
            _id=_id
        )