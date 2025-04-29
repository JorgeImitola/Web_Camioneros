import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from fastapi import APIRouter, HTTPException, status
from typing import List
from models import CamioneroBase, CamioneroUpdate
from db import camioneros_collection, camiones_collection, paquetes_collection, ciudades_collection

router = APIRouter(prefix="/camioneros", tags=["Camioneros"])

@router.get("/", response_model=List[CamioneroBase])
async def listar_camioneros():
    camioneros = []
    async for camionero in camioneros_collection.find():
        camioneros.append(camionero)
    return camioneros

@router.get("/{rfc}")
async def obtener_camionero(rfc: str):
    camionero = await camioneros_collection.find_one({"_id": rfc})
    if not camionero:
        raise HTTPException(status_code=404, detail="Camionero no encontrado")
    return {"mensaje": "Camionero encontrado", "camionero": camionero}

@router.post("/")
async def crear_camionero(camionero: CamioneroBase):
    if await camioneros_collection.find_one({"_id": camionero.id}):
        raise HTTPException(status_code=400, detail="Camionero ya existe")
    
    await camioneros_collection.insert_one(camionero.model_dump(by_alias=True))
    return {"mensaje": "Camionero creado", "camionero": camionero}

@router.put("/{rfc}")
async def actualizar_camionero(rfc: str, update_data: CamioneroUpdate):
    camionero = await camioneros_collection.find_one({"_id": rfc})
    if not camionero:
        raise HTTPException(status_code=404, detail="Camionero no encontrado")
    
    update_values = {k: v for k, v in update_data.model_dump().items() if v is not None}
    await camioneros_collection.update_one({"_id": rfc}, {"$set": update_values})
    
    camionero_actualizado = await camioneros_collection.find_one({"_id": rfc})
    return {"mensaje": "Camionero actualizado", "camionero": camionero_actualizado}

# Metodo para eliminar camioneros
@router.delete("/{rfc}")
async def eliminar_camionero(rfc: str):
    camionero = await camioneros_collection.find_one({"_id": rfc})
    if not camionero:
        raise HTTPException(status_code=404, detail="Camionero no encontrado")

    # Eliminar el camionero
    await camioneros_collection.delete_one({"_id": rfc})

    # Eliminar el conductor en todos los camiones donde aparezca
    await camiones_collection.update_many(
        {"conductores": rfc},
        {"$pull": {"conductores": rfc}}
    )

    return {"mensaje": f"Camionero {rfc} eliminado correctamente y referencias en camiones actualizadas."}

# Consulta 3
@router.get("/detalle/{rfc}")
async def detalle_camioneros(rfc: str):
    camionero = await camioneros_collection.find_one({"_id": rfc})
    if not camionero:
        raise HTTPException(status_code=404, detail="Camionero no encontrado")
    
    # Buscar los paquetes asignados a ese camionero
    paquetes = []
    async for paquete in paquetes_collection.find({"camionero_asignado": rfc}):
        # Buscar la ciudad del paquete
        ciudad = await ciudades_collection.find_one({"_id": paquete["ciudad_destino"]})
        nombre_ciudad = ciudad["nombre"] if ciudad else "Ciudad desconocida"

        paquetes.append({
            "descripcion_paquete": paquete["descripcion"],
            "direccion_destinatario": paquete["dir_destinatario"],
            "ciudad_destino": nombre_ciudad
        })

    return {
        "camionero": camionero["nombre"],
        "camiones_asignados": camionero.get("camiones_asignados", []),
        "paquetes": paquetes
    }