# Guía de Pruebas con Postman

Esta guía describe cómo probar los endpoints clave del backend para el flujo principal de la aplicación.

**Configuración Base:**
- Todos los endpoints asumen que la URL base es `http://127.0.0.1:5000`.
- Todas las solicitudes que envían datos (POST/PUT) deben tener el header `Content-Type` configurado en `application/json`.

---

### 1. Crear un Usuario (Alumno)

- **Método:** `POST`
- **URL:** `/usuarios/`
- **Descripción:** Registra un nuevo usuario en el sistema.

**Cuerpo (Body) - `raw (JSON)`:**
```json
{
    "usuario_id": "alumno_01",
    "nombre": "Juan",
    "apellido": "Perez",
    "correo": "juan.perez@email.com",
    "contraseña": "password123",
    "rol": "Alumno",
    "grado": "5",
    "seccion": "A"
}
```

**Respuesta Exitosa (201 Created):**
```json
{
    "msg": "Usuario creado exitosamente",
    "usuario_id": "alumno_01"
}
```

---

### 2. Crear una Evaluación

- **Método:** `POST`
- **URL:** `/evaluaciones/`
- **Descripción:** Permite a un docente crear una nueva evaluación con sus preguntas.

**Cuerpo (Body) - `raw (JSON)`:**
```json
{
    "titulo": "Examen de Matemáticas - 1er Trimestre",
    "materia": "Matemáticas",
    "grado": "5",
    "seccion": "A",
    "docente_id": "docente_01",
    "fecha_entrega": "2025-10-15T23:59:59",
    "intentos_permitidos": 2,
    "preguntas": [
        {
            "tipo": "OM",
            "enunciado": "¿Cuánto es 2 + 2?",
            "opciones": ["3", "4", "5"],
            "respuesta_correcta": "4"
        },
        {
            "tipo": "VF",
            "enunciado": "La Tierra es plana.",
            "opciones": ["Verdadero", "Falso"],
            "respuesta_correcta": "Falso"
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
*(Nota: Guarda el `evaluacion_id` para los siguientes pasos.)*

---

### 3. Listar Evaluaciones para un Alumno

- **Método:** `GET`
- **URL:** `/evaluaciones/grado/5/seccion/A`
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
        "docente_id": "docente_01",
        "fecha_creacion": "...",
        "fecha_entrega": "...",
        "estado": "activa",
        "intentos_permitidos": 2,
        "preguntas": [
            {
                "pregunta_id": "<ID_PREGUNTA_1>",
                "tipo": "OM",
                "enunciado": "¿Cuánto es 2 + 2?",
                "opciones": ["3", "4", "5"],
                "respuesta_correcta": "4"
            },
            "..."
        ]
    }
]
```

---

### 4. Iniciar un Intento de Evaluación

- **Método:** `POST`
- **URL:** `/intentos/`
- **Descripción:** Registra que un alumno ha comenzado a resolver una evaluación.

**Cuerpo (Body) - `raw (JSON)`:**
```json
{
    "evaluacion_id": "<ID_DE_LA_EVALUACION_DEL_PASO_2>",
    "alumno_id": "alumno_01"
}
```

**Respuesta Exitosa (201 Created):**
```json
{
    "intento_id": "<ID_DEL_INTENTO_GENERADO>",
    "evaluacion_id": "<ID_DE_LA_EVALUACION_DEL_PASO_2>",
    "alumno_id": "alumno_01",
    "fecha_inicio": "...",
    "fecha_fin": null,
    "calificacion": null,
    "estado": "en progreso",
    "respuestas": []
}
```
*(Nota: Guarda el `intento_id` para el siguiente paso.)*

---

### 5. Finalizar un Intento de Evaluación

- **Método:** `PUT`
- **URL:** `/intentos/<ID_DEL_INTENTO_DEL_PASO_4>/finalizar`
- **Descripción:** Envía las respuestas del alumno, finaliza el intento y calcula la calificación.

**Cuerpo (Body) - `raw (JSON)`:**
```json
{
    "respuestas": [
        {
            "pregunta_id": "<ID_PREGUNTA_1>",
            "opcion_marcada": "4"
        },
        {
            "pregunta_id": "<ID_PREGUNTA_2>",
            "opcion_marcada": "Falso"
        }
    ]
}
```

**Respuesta Exitosa (200 OK):**
```json
{
    "msg": "Intento finalizado exitosamente",
    "calificacion": 20,
    "intento_id": "<ID_DEL_INTENTO_DEL_PASO_4>"
}
```

---

### 6. Obtener Reporte del Intento

- **Método:** `POST`
- **URL:** `/reportes/`
- **Descripción:** Crea un reporte vacío asociado a un intento (la IA lo llenaría después).

**Cuerpo (Body) - `raw (JSON)`:**
```json
{
    "intento_id": "<ID_DEL_INTENTO_DEL_PASO_4>"
}
```

**Respuesta Exitosa (201 Created):**
```json
{
    "reporte_id": "<ID_REPORTE_GENERADO>",
    "intento_id": "<ID_DEL_INTENTO_DEL_PASO_4>",
    "diagnostico_ia": null,
    "recomendaciones_ia": null,
    "retroalimentacion_docente": null,
    "fecha_creacion": "..."
}
```

- **Método:** `GET`
- **URL:** `/reportes/intento/<ID_DEL_INTENTO_DEL_PASO_4>`
- **Descripción:** Obtiene el reporte de un intento específico.

**Respuesta Exitosa (200 OK):**
```json
{
    "reporte_id": "<ID_REPORTE_GENERADO>",
    "intento_id": "<ID_DEL_INTENTO_DEL_PASO_4>",
    "diagnostico_ia": null,
    "recomendaciones_ia": null,
    "retroalimentacion_docente": null,
    "fecha_creacion": "..."
}
```
