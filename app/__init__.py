from flask import Flask
from pymongo import MongoClient
from flask_cors import CORS
import os
import certifi
from .models.grado import Grado

# Variable global para la conexión a MongoDB
db_client = None
db = None

def create_app():
    global db_client, db
    
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": ["http://localhost:4200","http://127.0.0.1:4200"]}})
    app.config['JSON_AS_ASCII'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-super-secret-key')

    # Configuración MongoDB Atlas
    mongo_uri = "mongodb+srv://admin:jW0DwZFZuWsTxXym@alberteinstein.lftfvkl.mongodb.net/plataforma_simulacros?retryWrites=true&w=majority&appName=AlbertEinstein"
    
    try:
        ca = certifi.where()
        db_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000, tlsCAFile=ca)
        db = db_client.plataforma_simulacros
        app.db = db  # Hacer la base de datos accesible desde app
        # Verificar conexión
        db_client.admin.command('ping')
        print("✅ Conexión exitosa a MongoDB Atlas")

        # Poblar grados si la colección está vacía
        if db.grados.count_documents({}) == 0:
            grados_iniciales = [
                {"nombre": "1°", "descripcion": "Primer grado de secundaria"},
                {"nombre": "2°", "descripcion": "Segundo grado de secundaria"},
                {"nombre": "3°", "descripcion": "Tercer grado de secundaria"},
                {"nombre": "4°", "descripcion": "Cuarto grado de secundaria"},
                {"nombre": "5°", "descripcion": "Quinto grado de secundaria"}
            ]
            for grado_data in grados_iniciales:
                grado = Grado(nombre=grado_data["nombre"], descripcion=grado_data["descripcion"], estado=True)
                db.grados.insert_one(grado.to_dict())
            print("✅ Grados iniciales poblados exitosamente.")
    except Exception as e:
        print(f"❌ Error conectando a MongoDB: {e}")
        print("La aplicación continuará sin base de datos")

    # Importar rutas
    from .routes.usuario_routes import usuario_bp
    from .routes.evaluacion_routes import evaluacion_bp
    from .routes.intento_routes import intento_bp
    from .routes.reporte_routes import reporte_bp
    from .routes.notificacion_routes import notificacion_bp
    from .routes.grado_routes import grado_bp
    from .routes.seccion_routes import seccion_bp
    from .routes.dashboard_routes import dashboard_bp

    # Registrar Blueprints
    app.register_blueprint(usuario_bp, url_prefix="/usuarios")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(evaluacion_bp, url_prefix="/evaluaciones")
    app.register_blueprint(intento_bp, url_prefix="/intentos")
    app.register_blueprint(reporte_bp, url_prefix="/reportes")
    app.register_blueprint(notificacion_bp, url_prefix="/notificaciones")
    app.register_blueprint(grado_bp, url_prefix="/grados")
    app.register_blueprint(seccion_bp, url_prefix="/secciones")

    return app
