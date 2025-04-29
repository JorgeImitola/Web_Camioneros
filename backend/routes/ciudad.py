import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from fastapi import APIRouter, HTTPException, status
from typing import List
from models import CiudadBase,CiudadUpdate
from db import ciudades_collection, paquetes_collection

router = APIRouter(prefix="/ciudades", tags=["Ciudades"])

@router.get("/", response_model=List[CiudadBase])
async def listar_ciudades():
    ciudades = []
    async for ciudad in ciudades_collection.find():
        ciudades.append(ciudad)
    return ciudades

# Consulta 4
@router.get("/sin_paquetes")
async def ciudades_sin_paquetes():
    # Buscar todos los códigos de ciudad destino en los paquetes
    codigos_con_paquetes = set()
    async for paquete in paquetes_collection.find({}, {"ciudad_destino": 1}):
        codigos_con_paquetes.add(paquete["ciudad_destino"])

    # Buscar todas las ciudades que NO están en los códigos de paquetes
    ciudades = []
    async for ciudad in ciudades_collection.find():
        if ciudad["_id"] not in codigos_con_paquetes:
            ciudades.append({
                "codigo": ciudad["_id"],
                "nombre": ciudad["nombre"]
            })

    return {
        "mensaje": "Ciudades sin paquetes asignados",
        "total_ciudades": len(ciudades),
        "ciudades": ciudades
    }

@router.get("/{codigo}")
async def obtener_ciudad(codigo: str):
    ciudad = await ciudades_collection.find_one({"_id": codigo})
    if not ciudad:
        raise HTTPException(status_code=404, detail="Ciudad no encontrada")
    return {"mensaje": "Ciudad encontrada", "ciudad": ciudad}

@router.post("/")
async def crear_ciudad(ciudad: CiudadBase):
    if await ciudades_collection.find_one({"_id": ciudad.id}):
        raise HTTPException(status_code=400, detail="Ciudad ya existe")
    
    await ciudades_collection.insert_one(ciudad.model_dump(by_alias=True))
    return {"mensaje": "Ciudad creada", "ciudad": ciudad}

@router.put("/{codigo}")
async def actualizar_ciudad(codigo: str, update_data: CiudadUpdate):
    ciudad = await ciudades_collection.find_one({"_id": codigo})
    if not ciudad:
        raise HTTPException(status_code=404, detail="Ciudad no encontrada")
    
    update_values = {k: v for k, v in update_data.model_dump().items() if v is not None}
    await ciudades_collection.update_one({"_id": codigo}, {"$set": update_values})
    
    ciudad_actualizada = await ciudades_collection.find_one({"_id": codigo})
    return {"mensaje": "Ciudad actualizada", "ciudad": ciudad_actualizada}

# Metodo para eliminar ciudades
@router.delete("/{codigo}")
async def eliminar_ciudad(codigo: str):
    ciudad = await ciudades_collection.find_one({"_id": codigo})
    if not ciudad:
        raise HTTPException(status_code=404, detail="Ciudad no encontrada")

    # Eliminar la ciudad
    await ciudades_collection.delete_one({"_id": codigo})

    # Eliminar los paquetes que tengan como destino esta ciudad
    await paquetes_collection.delete_many({"ciudad_destino": codigo})

    return {"mensaje": f"Ciudad {codigo} eliminada correctamente y paquetes asociados eliminados."}