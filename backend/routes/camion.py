from fastapi import APIRouter, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import List, Dict, Any
from models import CamionBase, CamionUpdate
from db import camiones_collection, camioneros_collection
from bson import ObjectId
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/camiones", tags=["Camiones"])
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def listar_camiones(request: Request):
    camiones = []
    async for camion in camiones_collection.find():
        # Obtener nombres de conductores
        conductores_info = []
        for conductor_id in camion.get("conductores", []):
            conductor = await camioneros_collection.find_one({"_id": conductor_id})
            if conductor:
                conductores_info.append(conductor.get("nombre", conductor_id))
        
        camiones.append({
            "_id": str(camion["_id"]),
            "placa": camion.get("placa", ""),
            "modelo": camion.get("modelo", ""),
            "tipo": camion.get("tipo", ""),
            "potencia": camion.get("potencia", ""),
            "conductores": ", ".join(conductores_info) if conductores_info else "Ninguno"
        })
    
    return templates.TemplateResponse("camiones.html", {
        "request": request,
        "camiones": camiones
    })

@router.post("/crear", response_class=RedirectResponse)
async def crear_camion(
    placa: str = Form(...),
    modelo: str = Form(...),
    tipo: str = Form(...),
    potencia: str = Form(...)
):
    # Verificar si la placa ya existe
    if await camiones_collection.find_one({"placa": placa}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un camión con esta placa"
        )
    
    nuevo_camion = {
        "placa": placa,
        "modelo": modelo,
        "tipo": tipo,
        "potencia": potencia,
        "conductores": []
    }
    
    await camiones_collection.insert_one(nuevo_camion)
    return RedirectResponse(url="/camiones", status_code=303)

@router.post("/editar/{camion_id}", response_class=RedirectResponse)
async def editar_camion(
    camion_id: str,
    placa: str = Form(...),
    modelo: str = Form(...),
    tipo: str = Form(...),
    potencia: str = Form(...)
):
    # Verificar que el camión existe
    camion = await camiones_collection.find_one({"_id": ObjectId(camion_id)})
    if not camion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camión no encontrado"
        )
    
    # Verificar si la nueva placa ya existe (excepto para este camión)
    if placa != camion.get("placa", ""):
        if await camiones_collection.find_one({"placa": placa, "_id": {"$ne": ObjectId(camion_id)}}):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe otro camión con esta placa"
            )
    
    # Actualizar el camión
    await camiones_collection.update_one(
        {"_id": ObjectId(camion_id)},
        {"$set": {
            "placa": placa,
            "modelo": modelo,
            "tipo": tipo,
            "potencia": potencia
        }}
    )
    
    return RedirectResponse(url="/camiones", status_code=303)

@router.post("/eliminar/{camion_id}", response_class=RedirectResponse)
async def eliminar_camion(camion_id: str):
    # Verificar que el camión existe
    camion = await camiones_collection.find_one({"_id": ObjectId(camion_id)})
    if not camion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camión no encontrado"
        )
    
    # Eliminar referencias en camioneros
    await camioneros_collection.update_many(
        {"camiones_asignados": camion["placa"]},
        {"$pull": {"camiones_asignados": camion["placa"]}}
    )
    
    # Eliminar el camión
    await camiones_collection.delete_one({"_id": ObjectId(camion_id)})
    
    return RedirectResponse(url="/camiones", status_code=303)

@router.get("/disponibles", response_model=List[Dict[str, Any]])
async def listar_camiones_disponibles():
    camiones = []
    async for camion in camiones_collection.find({}, {"placa": 1, "modelo": 1}):
        camiones.append({
            "placa": camion["placa"],
            "modelo": camion.get("modelo", "")
        })
    return camiones