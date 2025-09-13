from app import db

class Pregunta(db.EmbeddedDocument):
    pregunta_id = db.StringField(required=True)
    tipo = db.StringField(required=True, choices=["OM", "VF"])
    enunciado = db.StringField(required=True)
    opciones = db.ListField(db.StringField())
    respuesta_correcta = db.StringField(required=True)

class Evaluacion(db.Document):
    evaluacion_id = db.StringField(required=True, unique=True)
    titulo = db.StringField(required=True)
    materia = db.StringField(required=True)
    grado = db.StringField(required=True)
    seccion = db.StringField(required=True)
    docente_id = db.StringField(required=True)
    fecha_creacion = db.DateTimeField()
    fecha_entrega = db.DateTimeField()
    estado = db.StringField(default="activa")
    intentos_permitidos = db.IntField(default=1)
    preguntas = db.ListField(db.EmbeddedDocumentField(Pregunta))
