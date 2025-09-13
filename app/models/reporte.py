from app import db

class Reporte(db.Document):
    reporte_id = db.StringField(required=True, unique=True)
    intento_id = db.StringField(required=True)
    diagnostico_ia = db.StringField()
    recomendaciones_ia = db.StringField()
    retroalimentacion_docente = db.StringField()
