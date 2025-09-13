from app import create_app
from app.models.usuario import Usuario

app = create_app()

if __name__ == "__main__":
    try:
        u = Usuario(
            nombre="Juan",
            apellido="Pérez",
            correo="juan@correo.com",
            rol="Alumno",
            grado="3",
            seccion="B"
        )
        u.save()
        print("✅ Usuario creado en Atlas:", u.to_json())

    except Exception as e:
        print("❌ Error:", e)

    app.run(debug=True)