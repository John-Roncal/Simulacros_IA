from flask import Blueprint, request, jsonify, current_app
from app.models.usuario import Usuario
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone

usuario_bp = Blueprint("usuarios", __name__)

@usuario_bp.route("/crear/alumno", methods=["POST"])
def crear_alumno():
    try:
        data = request.json
        required_fields = ["nombre", "apellido", "correo", "contraseña", "grado", "seccion"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo requerido faltante: {field}"}), 400

        if Usuario.find_by_email(data["correo"]):
            return jsonify({"error": "Correo electrónico ya registrado"}), 400

        hashed_password = bcrypt.hashpw(data["contraseña"].encode('utf-8'), bcrypt.gensalt())

        nuevo_alumno = Usuario(
            nombre=data["nombre"],
            apellido=data["apellido"],
            correo=data["correo"],
            contraseña_hash=hashed_password,
            rol="Alumno",
            grado=data["grado"],
            seccion=data["seccion"]
        )
        
        nuevo_alumno.save()
        return jsonify({"msg": "Alumno creado exitosamente", "usuario_id": nuevo_alumno.usuario_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@usuario_bp.route("/crear/docente", methods=["POST"])
def crear_docente():
    try:
        data = request.json
        required_fields = ["nombre", "apellido", "correo", "contraseña", "grado", "seccion"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo requerido faltante: {field}"}), 400

        if Usuario.find_by_email(data["correo"]):
            return jsonify({"error": "Correo electrónico ya registrado"}), 400

        hashed_password = bcrypt.hashpw(data["contraseña"].encode('utf-8'), bcrypt.gensalt())
        
        nuevo_docente = Usuario(
            nombre=data["nombre"],
            apellido=data["apellido"],
            correo=data["correo"],
            contraseña_hash=hashed_password,
            rol="Docente",
            grado=data["grado"],
            seccion=data["seccion"]
        )
        
        nuevo_docente.save()
        return jsonify({"msg": "Docente creado exitosamente", "usuario_id": nuevo_docente.usuario_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@usuario_bp.route("/crear/admin", methods=["POST"])
def crear_admin():
    try:
        data = request.json
        required_fields = ["nombre", "apellido", "correo", "contraseña"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo requerido faltante: {field}"}), 400

        if Usuario.find_by_email(data["correo"]):
            return jsonify({"error": "Correo electrónico ya registrado"}), 400

        hashed_password = bcrypt.hashpw(data["contraseña"].encode('utf-8'), bcrypt.gensalt())

        nuevo_admin = Usuario(
            nombre=data["nombre"],
            apellido=data["apellido"],
            correo=data["correo"],
            contraseña_hash=hashed_password,
            rol="Admin"
        )

        nuevo_admin.save()
        return jsonify({"msg": "Admin creado exitosamente", "usuario_id": nuevo_admin.usuario_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@usuario_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.json
        correo = data.get("correo")
        contraseña = data.get("contraseña")

        if not correo or not contraseña:
            return jsonify({"error": "Correo y contraseña son requeridos"}), 400

        usuario = Usuario.find_by_email(correo)

        if not usuario or not bcrypt.checkpw(contraseña.encode('utf-8'), usuario.contraseña_hash):
            return jsonify({"error": "Credenciales inválidas"}), 401

        token = jwt.encode({
            'usuario_id': usuario.usuario_id,
            'rol': usuario.rol,
            'exp': datetime.now(timezone.utc) + timedelta(hours=24)
        }, current_app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({'token': token, 'rol': usuario.rol, 'usuario_id': usuario.usuario_id}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@usuario_bp.route("/alumnos", methods=["GET"])
def listar_alumnos():
    try:
        alumnos = Usuario.find_by_role("Alumno")
        return jsonify([alumno.to_json() for alumno in alumnos]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@usuario_bp.route("/<int:usuario_id>", methods=["GET"])
def obtener_usuario(usuario_id):
    try:
        usuario = Usuario.find_by_id(usuario_id)
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404
        return jsonify(usuario.to_json()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@usuario_bp.route("/alumnos/<int:usuario_id>", methods=["GET"])
def obtener_alumno(usuario_id):
    try:
        alumno = Usuario.find_by_id(usuario_id)
        if not alumno or alumno.rol != 'Alumno':
            return jsonify({"error": "Alumno no encontrado"}), 404
        return jsonify(alumno.to_json()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@usuario_bp.route("/alumnos/<int:usuario_id>", methods=["PUT"])
def actualizar_alumno(usuario_id):
    try:
        data = request.json
        if "contraseña" in data:
            data["contraseña_hash"] = bcrypt.hashpw(data["contraseña"].encode('utf-8'), bcrypt.gensalt())
            del data["contraseña"]
        
        result = Usuario.update_by_id(usuario_id, data)
        if result.matched_count == 0:
            return jsonify({"error": "Alumno no encontrado"}), 404
        return jsonify({"msg": "Alumno actualizado exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@usuario_bp.route("/alumnos/<int:usuario_id>", methods=["DELETE"])
def anular_alumno(usuario_id):
    try:
        result = Usuario.update_by_id(usuario_id, {"estado": "inactivo"})
        if result.matched_count == 0:
            return jsonify({"error": "Alumno no encontrado"}), 404
        return jsonify({"msg": "Alumno anulado exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Rutas para Docentes
@usuario_bp.route("/docentes", methods=["GET"])
def listar_docentes():
    try:
        docentes = Usuario.find_by_role("Docente")
        return jsonify([docente.to_json() for docente in docentes]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@usuario_bp.route("/docentes/<int:usuario_id>", methods=["GET"])
def obtener_docente(usuario_id):
    try:
        docente = Usuario.find_by_id(usuario_id)
        if not docente or docente.rol != 'Docente':
            return jsonify({"error": "Docente no encontrado"}), 404
        return jsonify(docente.to_json()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@usuario_bp.route("/docentes/<int:usuario_id>", methods=["PUT"])
def actualizar_docente(usuario_id):
    try:
        data = request.json
        if "contraseña" in data:
            data["contraseña_hash"] = bcrypt.hashpw(data["contraseña"].encode('utf-8'), bcrypt.gensalt())
            del data["contraseña"]
        
        result = Usuario.update_by_id(usuario_id, data)
        if result.matched_count == 0:
            return jsonify({"error": "Docente no encontrado"}), 404
        return jsonify({"msg": "Docente actualizado exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@usuario_bp.route("/docentes/<int:usuario_id>", methods=["DELETE"])
def anular_docente(usuario_id):
    try:
        result = Usuario.update_by_id(usuario_id, {"estado": "inactivo"})
        if result.matched_count == 0:
            return jsonify({"error": "Docente no encontrado"}), 404
        return jsonify({"msg": "Docente anulado exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Rutas para Admins
@usuario_bp.route("/admins", methods=["GET"])
def listar_admins():
    try:
        admins = Usuario.find_by_role("Admin")
        return jsonify([admin.to_json() for admin in admins]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@usuario_bp.route("/admins/<int:usuario_id>", methods=["GET"])
def obtener_admin(usuario_id):
    try:
        admin = Usuario.find_by_id(usuario_id)
        if not admin or admin.rol != 'Admin':
            return jsonify({"error": "Admin no encontrado"}), 404
        return jsonify(admin.to_json()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@usuario_bp.route("/admins/<int:usuario_id>", methods=["PUT"])
def actualizar_admin(usuario_id):
    try:
        data = request.json
        if "contraseña" in data:
            data["contraseña_hash"] = bcrypt.hashpw(data["contraseña"].encode('utf-8'), bcrypt.gensalt())
            del data["contraseña"]
        
        result = Usuario.update_by_id(usuario_id, data)
        if result.matched_count == 0:
            return jsonify({"error": "Admin no encontrado"}), 404
        return jsonify({"msg": "Admin actualizado exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@usuario_bp.route("/admins/<int:usuario_id>", methods=["DELETE"])
def anular_admin(usuario_id):
    try:
        result = Usuario.update_by_id(usuario_id, {"estado": "inactivo"})
        if result.matched_count == 0:
            return jsonify({"error": "Admin no encontrado"}), 404
        return jsonify({"msg": "Admin anulado exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400