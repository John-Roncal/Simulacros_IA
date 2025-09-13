from app import db

class Respuesta(db.EmbeddedDocument):
    pregunta_id = db.StringField(required=True)
    opcion_marcada = db.StringField(required=True)
    es_correcta = db.BooleanField(default=False)

class Intento(db.Document):
    intento_id = db.StringField(required=True, unique=True)
    evaluacion_id = db.StringField(required=True)
    alumno_id = db.StringField(required=True)
    fecha_inicio = db.DateTimeField()
    fecha_fin = db.DateTimeField()
    calificacion = db.IntField()
    estado = db.StringField(default="en progreso")
    respuestas = db.ListField(db.EmbeddedDocumentField(Respuesta))
