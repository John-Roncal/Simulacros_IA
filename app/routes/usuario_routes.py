from flask import Blueprint, request, jsonify
from app.models.usuario import Usuario

usuario_bp = Blueprint("usuarios", __name__)

@usuario_bp.route("/", methods=["POST"])
def crear_usuario():
    data = request.json
    usuario = Usuario(**data)
    usuario.save()
    return jsonify({"msg": "Usuario creado exitosamente"}), 201

@usuario_bp.route("/", methods=["GET"])
def listar_usuarios():
    usuarios = Usuario.objects()
    return jsonify(usuarios), 200
