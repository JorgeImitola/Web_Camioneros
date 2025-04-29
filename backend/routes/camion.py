import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))# importar models y db desde la carpeta padre
from fastapi import APIRouter, HTTPException,status
from typing import List, Dict, Any
from models import CamionBase , CamionUpdate # <--- importar los modelos de datos
from db import camiones_collection, camioneros_collection


router = APIRouter(prefix="/camiones", tags=["Camiones"])
#LISTAR CAMIONES
@router.get("/", response_model=List[CamionBase])
async def listar_camiones():
    camiones = []
    async for camion in camiones_collection.find():
        camiones.append(camion)
    return camiones

# OBTENER CAMIÓN POR ID
@router.get("/{camion_id}")
async def obtener_camion(camion_id: str):
    camion = await camiones_collection.find_one({"_id": camion.id})
    if not camion:
        raise HTTPException(status_code=404, detail="Camión no encontrado")
    return {
        "mensaje": "Camión encontrado",
        "camion": camion
    }


# CREAR CAMIÓN
@router.post("/")
async def crear_camion(camion: CamionBase):
    # Revisa si ya existe
    camion_existente = await camiones_collection.find_one({"_id": camion.id})
    if camion_existente:
        raise HTTPException(status_code=400, detail="El camión ya existe")
    
    # Convertir el modelo a diccionario con "_id"
    camion_dict = camion.model_dump(by_alias=True)

    # Insertar usando "_id" como clave
    await camiones_collection.insert_one(camion_dict)

    return {
        "mensaje": "Camión creado",
        "camion": camion
    }

    
 
# ACTUALIZAR CAMIÓN
@router.put("/{camion_id}")
async def actualizar_camion(
    camion_id: str,
    update_data: CamionUpdate,
):
    """
    Parámetros:
        camion_id: ID del camión a actualizar (string)
        update_data: Campos a actualizar (modelo, tipo, potencia, conductores)
    """
    # Verificar si el camión existe
    camion_existente = await camiones_collection.find_one({"_id": camion_id})
    if not camion_existente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camion con ID {camion_id} no encontrado"
        )
    print(update_data)
    # Preparar datos de actualización (excluyendo campos no enviados)
    update_values = {k: v for k, v in update_data.model_dump().items() if v is not None}
    
    # Actualizar en la base de datos
    result = await camiones_collection.update_one(
        {"_id": camion_id},
        {"$set": update_values}
    )
    
    # Obtener y devolver el camión actualizado
    camion_actualizado = await camiones_collection.find_one({"_id": camion_id})
    
    return {
        "mensaje": "Camión actualizado correctamente",
        "camion": camion_actualizado
    }

# Metodo para eliminar camiones
@router.delete("/{camion_id}")
async def eliminar_camion(camion_id: str):
    camion = await camiones_collection.find_one({"_id": camion_id})
    if not camion:
        raise HTTPException(status_code=404, detail="Camión no encontrado")

    # Eliminar el camión
    await camiones_collection.delete_one({"_id": camion_id})

    # Eliminar el camión en la lista de camiones_asignados de los camioneros
    await camioneros_collection.update_many(
        {"camiones_asignados": camion_id},
        {"$pull": {"camiones_asignados": camion_id}}
    )

    return {"mensaje": f"Camión {camion_id} eliminado correctamente y referencias en camioneros actualizadas."}