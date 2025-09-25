# Guía de Pruebas con Postman

Esta guía describe cómo probar los endpoints clave del backend para el flujo principal de la aplicación.

**Configuración Base:**
- Todos los endpoints asumen que la URL base es `http://127.0.0.1:5000`.
- Todas las solicitudes que envían datos (POST/PUT) deben tener el header `Content-Type` configurado en `application/json`.

---

### 1. Gestión de Usuarios

#### 1.1 Crear un Usuario Alumno

- **Método:** `POST`
- **URL:** `/usuarios/crear/alumno`
- **Descripción:** Registra un nuevo alumno. El `usuario_id` es autoincremental.

**Cuerpo (Body) - `raw (JSON)`:**
```json
{
    "nombre": "Juan",
    "apellido": "Perez",
    "correo": "juan.perez@email.com",
    "contraseña": "password123",
    "grado": "5",
    "seccion": "A"
}
```

**Respuesta Exitosa (201 Created):**
```json
{
    "msg": "Alumno creado exitosamente",
    "usuario_id": 1
}
```

#### 1.2 Crear un Usuario Docente

- **Método:** `POST`
- **URL:** `/usuarios/crear/docente`
- **Descripción:** Registra un nuevo docente. El `usuario_id` es autoincremental.

**Cuerpo (Body) - `raw (JSON)`:**
```json
{
    "nombre": "Maria",
    "apellido": "Gonzalez",
    "correo": "maria.gonzalez@email.com",
    "contraseña": "password123",
    "grado": ["5", "6"],
    "seccion": ["A", "B"]
}
```

**Respuesta Exitosa (201 Created):**
```json
{
    "msg": "Docente creado exitosamente",
    "usuario_id": 2
}
```

#### 1.3 Crear un Usuario Admin

- **Método:** `POST`
- **URL:** `/usuarios/crear/admin`
- **Descripción:** Registra un nuevo administrador. El `usuario_id` es autoincremental.

**Cuerpo (Body) - `raw (JSON)`:**
```json
{
    "nombre": "Admin",
    "apellido": "Principal",
    "correo": "admin@email.com",
    "contraseña": "password123"
}
```

**Respuesta Exitosa (201 Created):**
```json
{
    "msg": "Admin creado exitosamente",
    "usuario_id": 3
}
```

#### 1.4 Listar, Actualizar y Anular Usuarios

- **Listar Alumnos:** `GET /usuarios/alumnos`
- **Obtener Alumno:** `GET /usuarios/alumnos/<usuario_id>`
- **Actualizar Alumno:** `PUT /usuarios/alumnos/<usuario_id>`
- **Anular Alumno:** `DELETE /usuarios/alumnos/<usuario_id>`

*(Lo mismo aplica para `/docentes` y `/admins`. El `<usuario_id>` será numérico para todos.)*

---

### 2. Gestión de Evaluaciones

#### 2.1 Crear una Evaluación

- **Método:** `POST`
- **URL:** `/evaluaciones/crear`
- **Descripción:** Permite a un docente crear una nueva evaluación.

**Cuerpo (Body) - `raw (JSON)`:**
```json
{
    "titulo": "Examen de Matemáticas - 1er Trimestre",
    "materia": "Matemáticas",
    "grado": "5",
    "seccion": "A",
    "docente_id": "2",
    "fecha_entrega": "2025-10-15T23:59:59",
    "intentos_permitidos": 2,
    "preguntas": [
        {
            "tipo": "OM",
            "enunciado": "¿Cuánto es 2 + 2?",
            "opciones": ["3", "4", "5"],
            "respuesta_correcta": "4"
        }
    ]
}
```

**Respuesta Exitosa (201 Created):**
```json
{
    "msg": "Evaluación creada exitosamente",
    "evaluacion_id": "<ID_DE_LA_EVALUACION_GENERADO>"
}
```

#### 2.2 Listar Evaluaciones con Filtros

- **Método:** `GET`
- **URL:** `/evaluaciones/listado?grado=5&seccion=A`
- **Descripción:** Obtiene todas las evaluaciones disponibles para un grado y sección específicos.

**Respuesta Exitosa (200 OK):**
```json
[
    {
        "evaluacion_id": "<ID_DE_LA_EVALUACION_GENERADO>",
        "titulo": "Examen de Matemáticas - 1er Trimestre",
        "materia": "Matemáticas",
        "grado": "5",
        "seccion": "A",
        "docente_id": "2",
        "..."
    }
]
```

---

### 3. Flujo de Intento de Evaluación (Sin cambios)

Los endpoints para iniciar, finalizar y obtener reportes de intentos no han cambiado.

- **Iniciar Intento:** `POST /intentos/`
- **Finalizar Intento:** `PUT /intentos/<intento_id>/finalizar`
- **Obtener Reporte:** `GET /reportes/intento/<intento_id>`