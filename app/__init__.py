from flask import Flask
from flask_mongoengine import MongoEngine

db = MongoEngine()

def create_app():
    app = Flask(__name__)

    # Configuración MongoDB (Atlas o Local)
    app.config["MONGODB_SETTINGS"] = {
        "db": "plataforma_simulacros",
        "host": "mongodb+srv://admin:jW0DwZFZuWsTxXym@alberteinstein.lftfvkl.mongodb.net/plataforma_simulacros?retryWrites=true&w=majority&appName=AlbertEinstein",
    }

    db.init_app(app)

    # Importar rutas
    from .routes.usuario_routes import usuario_bp
    from .routes.evaluacion_routes import evaluacion_bp
    from .routes.intento_routes import intento_bp
    from .routes.reporte_routes import reporte_bp

    # Registrar Blueprints
    app.register_blueprint(usuario_bp, url_prefix="/usuarios")
    app.register_blueprint(evaluacion_bp, url_prefix="/evaluaciones")
    app.register_blueprint(intento_bp, url_prefix="/intentos")
    app.register_blueprint(reporte_bp, url_prefix="/reportes")

    return app
