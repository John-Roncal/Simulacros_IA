from app import db

class Usuario(db.Document):
    usuario_id = db.StringField(required=True, unique=True)
    nombre = db.StringField(required=True)
    apellido = db.StringField(required=True)
    correo = db.StringField(required=True, unique=True)
    contraseña_hash = db.StringField(required=True)
    rol = db.StringField(required=True, choices=["Alumno", "Docente", "Admin"])
    grado = db.StringField()
    seccion = db.StringField()
    estado = db.StringField(default="activo")
