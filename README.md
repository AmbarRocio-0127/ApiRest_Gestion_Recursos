# API REST de Gestión de Recursos

API REST construida con **FastAPI** para administrar **recursos** (alta, consulta, actualización y baja) y que deja preparada la gestión de **usuarios**. El proyecto es un ejercicio de práctica de backend: en lugar de un CRUD mínimo, organiza el código con **routers por dominio**, **modelos de datos (DTO) con validación** y **respuestas HTTP explícitas**. Los datos viven **en memoria**, sin base de datos real.

---

## Contenido del repositorio

```
ApiRest_Gestion_Recursos/
├── main.py            # Modelos, almacenamiento en memoria, routers y endpoints
├── requirements.txt   # Dependencias del proyecto
└── README.md          # Este archivo
```

---

## Tecnologías

| Herramienta | Para qué se usa |
|---|---|
| **Python 3** | Lenguaje del proyecto |
| **FastAPI** | Framework web: rutas, validación de peticiones y documentación automática |
| **Uvicorn** | Servidor ASGI que ejecuta la aplicación |
| **Pydantic (v2)** | Modelos de datos y validación (`BaseModel`, `Field`) |

---

## Cómo está organizado el código

`main.py` se divide en cuatro bloques:

1. **Modelos (DTO):** clases que heredan de `BaseModel` y definen qué datos entran y salen de la API.
2. **Almacenamiento en memoria:** `db_recursos` y `db_usuario` (listas de diccionarios) y un contador de ids (`next_recurso_id`) que simula el autoincremento.
3. **Routers (`APIRouter`):** `recursos_router` (prefijo `/recursos`, etiqueta `APIRecursos`) y `usuarios_router` (etiqueta `APIUsuarios`).
4. **Endpoints:** funciones asíncronas decoradas con el método HTTP y la ruta que atienden.

### Modelos de datos

Cada entidad usa varios modelos, cada uno con un rol:

| Modelo | Rol |
|---|---|
| `RecursoBase` | Campos comunes del recurso, con sus validaciones |
| `RecursoCreate` | Entrada para crear un recurso (hereda de `RecursoBase`) |
| `RecursoUpdate` | Entrada para actualizar; todos los campos son opcionales |
| `RecursoResponse` | Salida; agrega `item_id`, el id que genera el servidor |
| `UsuarioBase` | Campos comunes del usuario, con sus validaciones |
| `UsuarioUpdate` | Entrada para actualizar un usuario; campos opcionales |
| `UsuarioResponse` | Salida; agrega `user_id` |

### Validaciones

| Campo | Regla |
|---|---|
| `nombre` (recurso) | Obligatorio, de 3 a 50 caracteres |
| `descripcion` (recurso) | Opcional, máximo 200 caracteres |
| `username` (usuario) | Obligatorio, de 4 a 16 caracteres |
| `email` (usuario) | Obligatorio, debe cumplir un patrón de correo válido |
| `edad` (usuario) | Obligatoria, mayor que 0 y menor que 120 |

Si un dato no cumple su regla, la API responde `422` sin ejecutar la lógica del endpoint.

---

## Endpoints de recursos

| Método | Ruta | Descripción | Respuesta exitosa |
|---|---|---|---|
| `POST` | `/recursos/` | Crear un recurso | `201 Created` |
| `GET` | `/recursos/` | Listar todos los recursos | `200 OK` |
| `GET` | `/recursos/{item_id}` | Obtener un recurso por ID | `200 OK` |
| `PUT` | `/recursos/{item_id}` | Actualizar un recurso (solo los campos enviados) | `200 OK` |
| `DELETE` | `/recursos/{item_id}` | Eliminar un recurso | `200 OK` |

**Errores:** `404 Not Found` si el recurso no existe y `422 Unprocessable Entity` si el ID o los datos no son válidos.

### Ejemplo

`POST /recursos/` con este cuerpo:

```json
{
  "nombre": "Monitor LG",
  "descripcion": "Monitor portátil para laptop"
}
```

Respuesta `201 Created`:

```json
{
  "nombre": "Monitor LG",
  "descripcion": "Monitor portátil para laptop",
  "item_id": 1
}
```

---

## Estado del proyecto

| Parte | Estado |
|---|---|
| Modelos de recursos y CRUD de recursos | Implementado |
| Modelos de usuarios y router de usuarios | Definidos |
| Endpoints de usuarios | Desarrollado |
| Instancia de la aplicación (`app = FastAPI(...)`) y registro de routers con `include_router` | Implementado |

---

## Instalación y ejecución

```bash
git clone https://github.com/AmbarRocio-0127/ApiRest_Gestion_Recursos.git
cd ApiRest_Gestion_Recursos
pip install -r requirements.txt
```

Una vez creada la instancia `app` en `main.py` y registrados los routers, el servidor se inicia con:

```bash
uvicorn main:app --reload
```

FastAPI genera la documentación interactiva en `http://127.0.0.1:8000/docs` (Swagger UI), donde se puede probar cada endpoint.

---

## Limitaciones

- Los datos se pierden al reiniciar el servidor (almacenamiento en memoria).
- No incluye autenticación, base de datos real ni pruebas automatizadas.

---

## Próximos pasos

- Crear la instancia de la aplicación y registrar los routers.
- Completar el CRUD de usuarios siguiendo la misma estructura que el de recursos.
- Reemplazar el almacenamiento en memoria por una base de datos.

---

Desarrollado por [Ámbar Rocío](https://github.com/AmbarRocio-0127) como práctica de backend con FastAPI.
