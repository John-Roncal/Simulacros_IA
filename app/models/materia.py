import app
from bson import ObjectId

class Materia:
    def __init__(self, nombre, estado="activo", materia_id=None, _id=None):
        self._id = _id if _id else ObjectId()
        self.materia_id = materia_id
        self.nombre = nombre
        self.estado = estado

    def save(self):
        if self.materia_id is None:
            self.materia_id = self.get_next_materia_id()

        materia_data = self.to_dict()
        if '_id' in materia_data and not self._id:
            del materia_data['_id']

        result = app.db.materias.insert_one(self.to_dict())
        self._id = result.inserted_id
        return result

    def to_dict(self):
        return {
            "materia_id": self.materia_id,
            "nombre": self.nombre,
            "estado": self.estado,
        }

    @classmethod
    def from_mongo(cls, data):
        if not data:
            return None
        return cls(
            _id=data.get('_id'),
            materia_id=data.get('materia_id'),
            nombre=data.get('nombre'),
            estado=data.get('estado')
        )

    @staticmethod
    def get_next_materia_id():
        last_materia = app.db.materias.find_one(
            {"materia_id": {"$type": ["double", "int", "long"]}},
            sort=[("materia_id", -1)]
        )
        if last_materia and isinstance(last_materia.get("materia_id"), (int, float)):
            return int(last_materia["materia_id"]) + 1
        return 1

    @staticmethod
    def find_all():
        return [Materia.from_mongo(materia_data) for materia_data in app.db.materias.find()]

    @staticmethod
    def find_by_id(materia_id):
        materia_data = app.db.materias.find_one({"materia_id": materia_id})
        return Materia.from_mongo(materia_data)

    @staticmethod
    def update_by_id(materia_id, update_data):
        return app.db.materias.update_one(
            {"materia_id": materia_id},
            {"$set": update_data}
        )

    @staticmethod
    def delete_by_id(materia_id):
        return app.db.materias.delete_one({"materia_id": materia_id})

    def to_json(self):
        data = self.to_dict()
        data['_id'] = str(self._id)
        return data
