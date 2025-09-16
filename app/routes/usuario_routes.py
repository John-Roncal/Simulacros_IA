from flask import Blueprint, request, jsonify
from app.models.usuario import Usuario
import hashlib

usuario_bp = Blueprint("usuarios", __name__)

@usuario_bp.route("/", methods=["POST"])
def crear_usuario():
    try:
        data = request.json
        
        # Validar campos requeridos
        required_fields = ["usuario_id", "nombre", "apellido", "correo", "contraseña", "rol"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo requerido faltante: {field}"}), 400
        
        # Verificar si el usuario ya existe
        if Usuario.find_by_id(data["usuario_id"]) or Usuario.find_by_email(data["correo"]):
            return jsonify({"error": "Usuario ya existe"}), 400
        
        # Hash de la contraseña
        password_hash = hashlib.sha256(data["contraseña"].encode()).hexdigest()
        
        # Crear usuario
        usuario = Usuario(
            usuario_id=data["usuario_id"],
            nombre=data["nombre"],
            apellido=data["apellido"],
            correo=data["correo"],
            contraseña_hash=password_hash,
            rol=data["rol"],
            grado=data.get("grado"),
            seccion=data.get("seccion")
        )
        
        usuario.save()
        return jsonify({"msg": "Usuario creado exitosamente", "usuario_id": usuario.usuario_id}), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@usuario_bp.route("/", methods=["GET"])
def listar_usuarios():
    try:
        usuarios = Usuario.find_all()
        # Convertir ObjectId a string para JSON
        for usuario in usuarios:
            if '_id' in usuario:
                usuario['_id'] = str(usuario['_id'])
        return jsonify(usuarios), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@usuario_bp.route("/<usuario_id>", methods=["GET"])
def obtener_usuario(usuario_id):
    try:
        usuario = Usuario.find_by_id(usuario_id)
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        if '_id' in usuario:
            usuario['_id'] = str(usuario['_id'])
        return jsonify(usuario), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@usuario_bp.route("/<usuario_id>", methods=["PUT"])
def actualizar_usuario(usuario_id):
    try:
        data = request.json
        
        # Si se actualiza la contraseña, hashearla
        if "contraseña" in data:
            data["contraseña_hash"] = hashlib.sha256(data["contraseña"].encode()).hexdigest()
            del data["contraseña"]  # Remover la contraseña plana
        
        result = Usuario.update_by_id(usuario_id, data)
        
        if result.matched_count == 0:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        return jsonify({"msg": "Usuario actualizado exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@usuario_bp.route("/<usuario_id>", methods=["DELETE"])
def eliminar_usuario(usuario_id):
    try:
        result = Usuario.delete_by_id(usuario_id)
        
        if result.deleted_count == 0:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        return jsonify({"msg": "Usuario eliminado exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400