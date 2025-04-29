import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any
from models import PaqueteBase, PaqueteUpdate
from db import paquetes_collection, camioneros_collection
from datetime import datetime

router = APIRouter(prefix="/paquetes", tags=["Paquetes"])

@router.get("/", response_model=List[PaqueteBase])
async def listar_paquetes():
    paquetes = []
    async for paquete in paquetes_collection.find():
        paquetes.append(paquete)
    return paquetes

@router.get("/{codigo}")
async def obtener_paquete(codigo: str):
    paquete = await paquetes_collection.find_one({"_id": codigo})
    if not paquete:
        raise HTTPException(status_code=404, detail="Paquete no encontrado")
    return {"mensaje": "Paquete encontrado", "paquete": paquete}

@router.post("/")
async def crear_paquete(paquete: PaqueteBase):
    if await paquetes_collection.find_one({"_id": paquete.id}):
        raise HTTPException(status_code=400, detail="Paquete ya existe")
    
    paquete_dict = paquete.model_dump(by_alias=True)
    await paquetes_collection.insert_one(paquete_dict)
    return {"mensaje": "Paquete creado", "paquete": paquete}

@router.put("/{codigo}")
async def actualizar_paquete(codigo: str, update_data: PaqueteUpdate):
    paquete = await paquetes_collection.find_one({"_id": codigo})
    if not paquete:
        raise HTTPException(status_code=404, detail="Paquete no encontrado")
    
    update_values = {k: v for k, v in update_data.model_dump().items() if v is not None}
    if 'fecha_entrega' in update_values:
        update_values['fecha_entrega'] = datetime.now()
    
    await paquetes_collection.update_one({"_id": codigo}, {"$set": update_values})
    
    paquete_actualizado = await paquetes_collection.find_one({"_id": codigo})
    return {"mensaje": "Paquete actualizado", "paquete": paquete_actualizado}

#Asignar camionero a paquete
@router.post("/Asignar camionero a paquete/{camionero_id}/{paquete_id}", )
async def asignar_paquete(camionero_id: str, paquete_id: str):
    camionero = await camioneros_collection.find_one({"_id": camionero_id})
    if not camionero:
        raise HTTPException(status_code=404, detail="Camionero no encontrado")
    
    paquete = await paquetes_collection.find_one({"_id": paquete_id})
    if not paquete:
        raise HTTPException(status_code=404, detail="Paquete no encontrado")
    
    # Asignar el paquete al camionero
    paquete=await paquetes_collection.update_one({"_id": paquete_id}, {"$set": {"camionero_asignado": camionero_id}})
    paquete = await paquetes_collection.find_one({"_id": paquete_id})
    return {"mensaje": "Paquete asignado correctamente", "Paquete": paquete}   
    return {"mensaje": "Paquetes encontrados", "paquetes": paquetes}
@router.get("/camionero/total")
async def total_paquetes():
    total_paquetes = await paquetes_collection.count_documents({})
    return {"mensaje": "Total de paquetes", "total": total_paquetes}