from bson.objectid import ObjectId

class Grado:
    def __init__(self, nombre, descripcion, estado=True, _id=None):
        self.nombre = nombre
        self.descripcion = descripcion
        self.estado = estado
        self._id = _id if _id else ObjectId()

    def to_dict(self):
        """Retorna dict listo para insertar/actualizar en MongoDB (tipos nativos)."""
        return {
            "_id": self._id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "estado": self.estado
        }

    def to_json(self):
        """Retorna dict serializable a JSON (id como string)."""
        return {
            "_id": str(self._id),
            "nombre": self.nombre,
            "descripcion": self.descripcion,
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
        """Crea instancia Grado desde documento Mongo (acepta _id como str u ObjectId)."""
        _id = Grado._ensure_objectid(data.get('_id'))
        return Grado(
            nombre=data.get('nombre'),
            descripcion=data.get('descripcion'),
            estado=data.get('estado', True),
            _id=_id
        )