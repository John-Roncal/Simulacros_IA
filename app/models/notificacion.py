from app import db

class Notificacion(db.Document):
    notificacion_id = db.StringField(required=True, unique=True)
    usuario_id = db.StringField(required=True)
    mensaje = db.StringField(required=True)
    fecha = db.DateTimeField()
    tipo = db.StringField(choices=["alerta", "aviso", "recordatorio"])
    estado = db.StringField(default="no leído")