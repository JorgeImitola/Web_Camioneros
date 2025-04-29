import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from fastapi import APIRouter, HTTPException, status
from typing import List
from models import CamioneroBase, CamioneroUpdate
from db import camioneros_collection, camiones_collection, paquetes_collection, ciudades_collection
from typing import Dict, List
router = APIRouter(prefix="/camioneros", tags=["Camioneros"])
#Consulta2
@router.get("/", response_model=List[CamioneroBase])
async def listar_camioneros():
    camioneros = []
    async for camionero in camioneros_collection.find():
        camioneros.append(camionero)
    return camioneros

@router.get("/camioneros-camiones")
async def listar_camioneros_con_camiones():
    resultado = []

    async for camionero in camioneros_collection.find():
        rfc = camionero.get("_id")
        nombre = camionero.get("nombre")
        camiones_asignados = camionero.get("camiones_asignados", [])

        resultado.append({
            "rfc": rfc,
            "nombre": nombre,
            "camiones": camiones_asignados
        })

    return resultado

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

#ASIGNAR CAMION A CAMIONERO
@router.post("/{camion_id}/{camionero_id}")
async def asignar_camion(camionero_id: str, camion_id: str):
    camionero = await camioneros_collection.find_one({"_id": camionero_id})
    if not camionero:
        raise HTTPException(status_code=404, detail="Camionero no encontrado")
    camion= await camiones_collection.find_one({"_id": camion_id})
    if not camion:
        raise HTTPException(status_code=404, detail="Camion no encontrado")
    await camioneros_collection.update_one({"_id": camionero_id}, {"$addToSet": {"camiones_asignados": camion_id}})
    await camiones_collection.update_one({"_id": camion_id}, {"$addToSet": {"conductores": camionero_id}})
    camionero_actualizado = await camioneros_collection.find_one({"_id": camionero_id})
    return {"mensaje": "Camion asignado correctamente",  "camionero": camionero_actualizado}





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

#CONSULTA1
#Cantidad de paquetes por camionero
@router.get("/camionero/{rfc}")
async def paquetes_por_camionero(rfc: str):
    paquetes = []
   
    async for paquete in paquetes_collection.find({"camionero_asignado": rfc}):
        paquetes.append(paquete)
    total_paquetes = len(paquetes)
    return {
        "mensaje": f"Paquetes encontrados para el camionero {rfc}",
        "total_paquetes": total_paquetes,
        "paquetes": paquetes
    }

