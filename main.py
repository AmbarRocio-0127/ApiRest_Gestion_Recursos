from fastapi import FastAPI, APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class RecursoBase(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=50, description="Nombre de Recurso", examples=["Monitor LG"])
    descripcion: Optional[str] = Field(None, max_length=200, description="Descripcion opcional del recurso",
    examples=["Monitor portátil para laptop"])
    
class RecursoCreate(RecursoBase):
    pass

class RecursoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=3, max_length=50, examples=["Recurso Actualizado"])
    descripcion: Optional[str] = Field(None, max_length=200, description="Descripcion opcional del recurso", examples=["Nueva Descripcion"])
  
class RecursoResponse(RecursoBase):
    item_id : int = Field(..., gt=0, description="ID único del recurso")
    
class UsuarioBase(BaseModel):
    username: str = Field(..., min_length=4, max_length=16, description="Nombre de Usuario", examples=["Anne Marie Smith"])
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", description="Correo Electrónico Válido", 
            examples=["annemariesmith@example.com"])
    edad: int = Field(..., gt=0, lt=120, description="Edad entre 1 y 119 años", examples=[28])
    
class UsuarioUpdate(BaseModel):
    username: str = Field(None, min_length=4, max_length=16, examples=["Usuario Actualizado"])
    email: Optional[str] = Field(None, pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", examples=["annemariesmith@example.com"])
    edad: Optional[int] = Field(None, gt=0, lt=120, examples=[29])
    
class UsuarioResponse(UsuarioBase):
    user_id: int = Field(..., gt=0, description="ID único de usuario")
    
db_recursos: List[Dict] = []
next_recurso_id = 1

db_usuario: List[Dict] = []

recursos_router = APIRouter(
    prefix="/recursos",
    tags=["APIRecursos"],
    responses={404: {"descripcion": "Recurso no encontrado"}}
)

usuarios_router =  APIRouter(
    prefix="/recursos",
    tags=["APIUsuarios"],
    responses={404: {"descripcion": "Usuario no encontrado"}}
)

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

@recursos_router.get(
    "/",
    response_model=List[RecursoResponse],
    summary="Obtener todos los recursos"
)
async def get_all_recursos():
    return db_recursos

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
            update_data = recurso.model_dump(exclude_unset=True)
            item.update(update_data)
            return item
    raise HTTPException(status_code=404, detail="Recurso no encontrado")

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

#____________________________________________________________________________________________________________________________________________
#DESARROLLO DE LOS ENDPOINTS DE CRUD DE USUARIOS
#____________________________________________________________________________________________________________________________________________

app = FastAPI(
    title="Api Recursos y Usuarios",
    description="Ejemplo de APIs con FastAPI, APIRouter personalizados, validacion con pydantic y base en memoria",
    version="2.0.0"
)
@app.get("/", summary="Pasina de inicio de la API")
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