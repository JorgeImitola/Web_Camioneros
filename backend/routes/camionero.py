from fastapi import APIRouter, HTTPException, status, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from typing import List, Dict, Any, Optional
from models import CamioneroBase, CamioneroUpdate
from db import camioneros_collection, camiones_collection
from bson import ObjectId
from pydantic import ValidationError

router = APIRouter(prefix="/camioneros", tags=["Camioneros"])

# Helper function to convert ObjectId to string
def convert_objectid(data: dict) -> dict:
    if '_id' in data:
        data['_id'] = str(data['_id'])
    return data

@router.get("/", response_model=List[Dict[str, Any]])
async def listar_camioneros():
    camioneros = []
    async for camionero in camioneros_collection.find():
        # Obtener detalles de los camiones asignados
        camiones_asignados = []
        for camion_id in camionero.get("camiones_asignados", []):
            camion = await camiones_collection.find_one({"_id": camion_id})
            if camion:
                camiones_asignados.append(f"{camion.get('modelo', '')} ({camion_id})")
        
        camionero_data = {
            "_id": str(camionero["_id"]),
            "nombre": camionero.get("nombre", ""),
            "telefono": camionero.get("telefono", ""),
            "direccion": camionero.get("direccion", ""),
            "salario": camionero.get("salario", 0),
            "poblacion": camionero.get("poblacion", ""),
            "camiones_asignados": ", ".join(camiones_asignados) if camiones_asignados else "Ninguno"
        }
        camioneros.append(camionero_data)
    return camioneros

@router.get("/{rfc}", response_model=Dict[str, Any])
async def obtener_camionero(rfc: str):
    camionero = await camioneros_collection.find_one({"_id": rfc})
    if not camionero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camionero con RFC {rfc} no encontrado"
        )
    return convert_objectid(camionero)

@router.post("/agregar")
async def agregar_camionero(
    rfc: str = Form(...),
    nombre: str = Form(...),
    telefono: str = Form(...),
    direccion: str = Form(...),
    salario: float = Form(...),
    poblacion: str = Form(None),
    camiones_ids: List[str] = Form([])
):
    try:
        # Verificar si el camionero ya existe
        if await camioneros_collection.find_one({"_id": rfc}):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El camionero ya existe"
            )
        
        # Verificar que los camiones existen
        camiones_invalidos = []
        for camion_id in camiones_ids:
            if not await camiones_collection.find_one({"_id": camion_id}):
                camiones_invalidos.append(camion_id)
        
        if camiones_invalidos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Los siguientes IDs de camión no existen: {', '.join(camiones_invalidos)}"
            )
        
        # Crear el documento del camionero
        camionero = {
            "_id": rfc,
            "nombre": nombre,
            "telefono": telefono,
            "direccion": direccion,
            "salario": salario,
            "poblacion": poblacion,
            "camiones_asignados": camiones_ids
        }
        
        # Insertar en la base de datos
        await camioneros_collection.insert_one(camionero)
        
        # Asignar camiones (relación bidireccional)
        for camion_id in camiones_ids:
            await camiones_collection.update_one(
                {"_id": camion_id},
                {"$addToSet": {"conductores": rfc}}
            )
        
        return RedirectResponse(url="/Camioneros", status_code=status.HTTP_303_SEE_OTHER)
    
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/editar/{rfc}")
async def editar_camionero(
    rfc: str,
    nombre: str = Form(...),
    telefono: str = Form(...),
    direccion: str = Form(...),
    salario: float = Form(...),
    poblacion: str = Form(None),
    camiones_ids: List[str] = Form([])
):
    try:
        # Verificar que el camionero existe
        camionero = await camioneros_collection.find_one({"_id": rfc})
        if not camionero:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Camionero no encontrado"
            )
        
        # Verificar que los camiones existen
        camiones_invalidos = []
        for camion_id in camiones_ids:
            if not await camiones_collection.find_one({"_id": camion_id}):
                camiones_invalidos.append(camion_id)
        
        if camiones_invalidos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Los siguientes IDs de camión no existen: {', '.join(camiones_invalidos)}"
            )
        
        # Obtener camiones asignados actuales
        camiones_actuales = camionero.get("camiones_asignados", [])
        
        # Actualizar datos básicos
        await camioneros_collection.update_one(
            {"_id": rfc},
            {"$set": {
                "nombre": nombre,
                "telefono": telefono,
                "direccion": direccion,
                "salario": salario,
                "poblacion": poblacion,
                "camiones_asignados": camiones_ids
            }}
        )
        
        # Manejar asignación de camiones (relación bidireccional)
        
        # 1. Camiones que hay que quitar (estaban asignados pero ya no)
        camiones_a_quitar = list(set(camiones_actuales) - set(camiones_ids))
        for camion_id in camiones_a_quitar:
            await camiones_collection.update_one(
                {"_id": camion_id},
                {"$pull": {"conductores": rfc}}
            )
        
        # 2. Camiones que hay que agregar (no estaban asignados pero ahora sí)
        camiones_a_agregar = list(set(camiones_ids) - set(camiones_actuales))
        for camion_id in camiones_a_agregar:
            await camiones_collection.update_one(
                {"_id": camion_id},
                {"$addToSet": {"conductores": rfc}}
            )
        
        return RedirectResponse(url="/Camioneros", status_code=status.HTTP_303_SEE_OTHER)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/eliminar/{rfc}")
async def eliminar_camionero(rfc: str):
    # Verificar existencia
    camionero = await camioneros_collection.find_one({"_id": rfc})
    if not camionero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camionero no encontrado"
        )
    
    # Eliminar referencias en camiones
    camiones_asignados = camionero.get("camiones_asignados", [])
    for camion_id in camiones_asignados:
        await camiones_collection.update_one(
            {"_id": camion_id},
            {"$pull": {"conductores": rfc}}
        )
    
    # Eliminar camionero
    await camioneros_collection.delete_one({"_id": rfc})
    
    return RedirectResponse(url="/Camioneros", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/camiones/disponibles", response_model=List[Dict[str, Any]])
async def listar_camiones_disponibles():
    camiones = []
    async for camion in camiones_collection.find({}, {"_id": 1, "modelo": 1, "placa": 1}):
        camiones.append({
            "_id": str(camion["_id"]),
            "modelo": camion.get("modelo", ""),
            "placa": camion.get("placa", "")
        })
    return camiones