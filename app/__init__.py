from flask import Flask
from pymongo import MongoClient
import os

# Variable global para la conexión a MongoDB
db_client = None
db = None

def create_app():
    global db_client, db
    
    app = Flask(__name__)

    # Configuración MongoDB Atlas
    mongo_uri = "mongodb+srv://admin:jW0DwZFZuWsTxXym@alberteinstein.lftfvkl.mongodb.net/plataforma_simulacros?retryWrites=true&w=majority&appName=AlbertEinstein"
    
    try:
        db_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        db = db_client.plataforma_simulacros
        # Verificar conexión
        db_client.admin.command('ping')
        print("✅ Conexión exitosa a MongoDB Atlas")
    except Exception as e:
        print(f"❌ Error conectando a MongoDB: {e}")
        print("La aplicación continuará sin base de datos")

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