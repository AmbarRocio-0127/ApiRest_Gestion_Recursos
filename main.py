""" Importacion de librerias necesarias"""

from fastapi import FastAPI, APIRouter, HTTPException, status #APIRouter agrupa endpoints por módulo, 
#HTTPException devuelve errores HTTP (404, 422) y status ofrece constantes de códigos HTTP
from fastapi.responses import JSONResponse ## JSONResponse: permite devolver respuestas JSON personalizadas
# Pydantic: BaseModel es la clase base de los modelos (DTO) que validan los datos,
# y Field agrega restricciones y metadatos a cada campo (longitud, rango, descripción, ejemplos).
from pydantic import BaseModel, Field 
# typing: anotaciones de tipo. List (lista), Dict (diccionario) y Optional (valor que puede ser None).
from typing import List, Dict, Optional

#  Modelo de datos para crear los recursos (Heredando de la clase base BaseModel, responsable de la creación de dichos modelos)
class RecursoBase(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=50, description="Nombre de Recurso", examples=["Monitor LG"])
    descripcion: Optional[str] = Field(None, max_length=200, description="Descripcion opcional del recurso",
    examples=["Monitor portátil para laptop"])
    categoria: str = Field(...,min_length=6, max_length=30, description="categoria")
    cantidad: int = Field(..., ge=0, description="Cantidad") # ge para que sea mayor o igual a cero
    precio: float = Field(...,ge=0, description="$00.00")
    
# DTO de entrada para crear un recurso (POST). Hereda los campos de RecursoBase
# (nombre y descripcion) con sus validaciones;
class RecursoCreate(RecursoBase):
    pass

#  Modelo de datos para modificar de los recursos (Heredando de la clase base BaseModel, responsable de la creación de dichos modelos)
class RecursoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=3, max_length=50, examples=["Recurso Actualizado"]) #field() añade metadatos y restricciones a cada campo.
    descripcion: Optional[str] = Field(None, max_length=200, description="Descripcion opcional del recurso", examples=["Nueva Descripcion"])
    categoria: str = Field(None,min_length=6, max_length=30)
    cantidad: int = Field(None, ge=0, description="Cantidad")
    precio: float = Field(None,ge=0, description="$00.00")
class RecursoResponse(RecursoBase):
    item_id : int = Field(..., gt=0, description="ID único del recurso")
    
#  Modelo de datos para crear los usuarios (Heredando de la clase base BaseModel, responsable de la creación de dichos modelos)
class UsuarioBase(BaseModel):
    username: str = Field(..., min_length=4, max_length=16, description="Nombre de Usuario", examples=["Anne Marie Smith"])
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", description="Correo Electrónico Válido", 
            examples=["annemariesmith@example.com"])
    edad: int = Field(..., gt=0, lt=120, description="Edad entre 1 y 119 años", examples=[28])

# DTO de entrada para crear un usuario (POST). Hereda los campos de UsuarioBase
# (username, email y edad) con sus validaciones;
class UsuarioCreate(UsuarioBase):
    pass

#  Modelo de datos para modificar los usuarios (Heredando de la clase base BaseModel, responsable de la creación de dichos modelos)
class UsuarioUpdate(BaseModel):
    username: str = Field(None, min_length=4, max_length=16, examples=["Usuario Actualizado"])
    email: Optional[str] = Field(None, pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", examples=["annemariesmith@example.com"])
    edad: Optional[int] = Field(None, gt=0, lt=120, examples=[29])
    
class UsuarioResponse(UsuarioBase):
    user_id: int = Field(..., gt=0, description="ID único de usuario")

# Estructura simulada para la persistencia de los datos
db_recursos: List[Dict] = []
db_usuario: List[Dict] = []

# Creacion para los id de los recursos y usuarios
next_recurso_id = 1
next_usuario_id = 1

recursos_router = APIRouter(
    prefix="/recursos",
    tags=["APIRecursos"],
    responses={404: {"descripcion": "Recurso no encontrado"}}
)

usuarios_router =  APIRouter(
    prefix="/usuarios",
    tags=["APIUsuarios"],
    responses={404: {"descripcion": "Usuario no encontrado"}}
)
"""endpoint para la creacion de un recurso"""
@recursos_router.post(
    "/",
    response_model=RecursoResponse,
    status_code= status.HTTP_201_CREATED,
    summary="Crear nuevo recurso"
)
async def create_recurso(recurso: RecursoCreate):
    global next_recurso_id
    new_item = recurso.model_dump()
    new_item["item_id"] = next_recurso_id
    db_recursos.append(new_item)
    next_recurso_id += 1
    return new_item

"""endpoint para el listado de todos los recursos"""
@recursos_router.get(
    "/",
    response_model=List[RecursoResponse],
    summary="Obtener todos los recursos"
)
async def get_all_recursos():
    return db_recursos

"""endpoint para el listado de un solo recurso"""
@recursos_router.get(
    "/{item_id}",
    response_model=RecursoResponse,
    summary="Obtener un recurso a traves de su ID"
)
async def read_recurso(item_id : int):
    if item_id <= 0:
        raise HTTPException(status_code=422, detail="ID de un recurso inválido")
    for item in db_recursos:
        if item["item_id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Recurso no encontrado")

"""endpoint para la actualizacion de un recurso"""
@recursos_router.put(
    "/{item_id}",
    response_model=RecursoResponse,
    summary="Actualizar un recurso existente"
)
async def update_recurso(item_id: int, recurso: RecursoUpdate):
    if item_id <= 0:
        raise HTTPException(status_code=422, detail="ID de un recurso Inválido")
    for item in db_recursos:
        if item["item_id"] == item_id:
            update_data = recurso.model_dump(exclude_unset=True) # modeldump() Devuelve un diccionario con los campos y valores del modelo
            item.update(update_data)
            return item
    raise HTTPException(status_code=404, detail="Recurso no encontrado")

"""endpoint para la eliminacion de un recurso"""
@recursos_router.delete(
    "/{item_id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar un recurso"
)
async def delete_recurso(item_id: int):
    global db_recursos
    for item in db_recursos:
        if item["item_id"] == item_id:
            db_recursos.remove(item)
            return {"mensaje": "Recurso eliminado correctamente"}
    raise HTTPException(status_code=404, detail="Recurso no encontrado")

"""____________________________________________________________________________________
   DESARROLLO DE LOS ENDPOINTS DE CRUD DE USUARIOS
   ____________________________________________________________________________________"""

"""----------------------------------------------------------------------
  INSTANCIA PRINCIPAL DE LA APLICACIÓN
  Crea la app de FastAPI. Uvicorn la carga como "main:app".
  title, description y version son metadatos que aparecen en la
  documentación automática (Swagger, en /docs).
  ----------------------------------------------------------------------"""
app = FastAPI(
    title="Api Recursos y Usuarios",
    description="Ejemplo de APIs con FastAPI, APIRouter personalizados, validacion con pydantic y base en memoria",
    version="2.0.0"
)

""" ENDPOINT RAIZ (GET /)
  Se define directamente sobre la app, no sobre un router, porque no
  pertenece a ningún recurso. Sirve como página de bienvenida: devuelve
  un JSON con la versión, la ruta de la documentación y las rutas
  principales de la API"""
  
@app.get("/", summary="Pagina de inicio de la API")
async def root():
    return{
        "mensaje": "Bienvenido a la API de Recursos y Usuarios",
        "version": "2.0.0",
        "documentacion": "/docs",
        "endpoints": {
            "recursos": "/recursos",
            "usuarios": "/usuarios"
        }
    }
""" REGISTRO DE ROUTERS
  Conecta los routers a la app. Sin este paso, los endpoints definidos
  en recursos_router y usuarios_router no existirían para el servidor.
  Cada uno aporta su prefijo (/recursos y /usuarios)."""
  
app.include_router(recursos_router)
app.include_router(usuarios_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload= True,
        log_level="info"
    )
    
"""endpoint para la creacion de un usuario"""
@usuarios_router.post(
    "/",
    response_model=UsuarioResponse,
    status_code= status.HTTP_201_CREATED,
    summary="Crear nuevo usuario"
)
async def create_usuario(usuario: UsuarioCreate):
    global next_usuario_id
    new_item = usuario.model_dump()
    new_item["user_id"] = next_usuario_id
    db_usuario.append(new_item)
    next_usuario_id += 1
    return new_item

"""endpoint para el listado de todos los usuarios"""
@usuarios_router.get(
    "/",
    response_model=List[UsuarioResponse],
    summary="Obtener todos los usuarios"
)
async def get_all_usuarios():
    return db_usuario

"""endpoint para el listado de un solo usuario"""
@usuarios_router.get(
    "/{user_id}",
    response_model=UsuarioResponse,
    summary="Obtener un usuario a traves de su ID"
)
async def read_usuario(item_id : int):
    if item_id <= 0:
        raise HTTPException(status_code=422, detail="ID de un usuario inválido")
    for item in db_usuario:
        if item["user_id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

"""endpoint para la modificar de un usuario"""
@usuarios_router.put(
    "/{user_id}",
    response_model=UsuarioResponse,
    summary="Modificar un usuario existente"
)
async def update_usuario(user_id: int, usuario: UsuarioUpdate):
    if user_id <= 0:
        raise HTTPException(status_code=422, detail="ID de un recurso Inválido")
    for user in db_usuario:
        if user["user_id"] == user_id:
            update_data = usuario.model_dump(exclude_unset=True) # modeldump() Devuelve un diccionario con los campos y valores del modelo
            user.update(update_data)
            return user
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

"""endpoint para la eliminacion de un usuario"""
@usuarios_router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar un usuario"
)
async def delete_usuario(user_id: int):
    global db_usuario
    for usuario in db_usuario:
        if usuario["user_id"] == user_id:
            db_usuario.remove(usuario)
            return {"mensaje": "Usuario eliminado correctamente"}
    raise HTTPException(status_code=404, detail="Usuario no encontrado")
