from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from db import (
    camiones_collection,
    paquetes_collection,
    camioneros_collection,
    ciudades_collection
)
from bson import ObjectId
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# ==============================================
# Funciones para Camioneros
# ==============================================
async def listar_camioneros() -> List[dict]:
    try:
        camioneros = await camioneros_collection.find().to_list(length=100)
        for camionero in camioneros:
            camionero["_id"] = str(camionero["_id"])
        return camioneros
    except Exception as e:
        print(f"Error al obtener camioneros: {e}")
        return []

async def obtener_camionero(rfc: str) -> Optional[dict]:
    try:
        camionero = await camioneros_collection.find_one({"_id": rfc})
        if camionero:
            camionero["_id"] = str(camionero["_id"])
            return camionero
        return None
    except Exception as e:
        print(f"Error al obtener camionero: {e}")
        return None

# ==============================================
# Funciones para Camiones
# ==============================================
async def listar_camiones():
    try:
        camiones = await camiones_collection.find().to_list(length=100)
        for camion in camiones:
            camion["_id"] = str(camion["_id"])
            # Obtener nombres de conductores
            if "conductores" in camion:
                conductores_info = []
                for rfc in camion["conductores"]:
                    conductor = await camioneros_collection.find_one({"_id": rfc})
                    if conductor:
                        conductores_info.append(conductor.get("nombre", rfc))
                camion["conductores_nombres"] = ", ".join(conductores_info) if conductores_info else "Ninguno"
            else:
                camion["conductores_nombres"] = "Ninguno"
        return camiones
    except Exception as e:
        print(f"Error al obtener camiones: {e}")
        return []

async def obtener_camion(camion_id: str):
    try:
        camion = await camiones_collection.find_one({"_id": ObjectId(camion_id)})
        if camion:
            camion["_id"] = str(camion["_id"])
            return camion
        return None
    except Exception as e:
        print(f"Error al obtener camión: {e}")
        return None

# ==============================================
# Funciones para Ciudades
# ==============================================
async def listar_ciudades() -> List[dict]:
    try:
        ciudades = await ciudades_collection.find().to_list(length=100)
        for ciudad in ciudades:
            ciudad["_id"] = str(ciudad["_id"])
        return ciudades
    except Exception as e:
        print(f"Error al obtener ciudades: {e}")
        return []

async def obtener_ciudad(ciudad_id: str) -> Optional[dict]:
    try:
        ciudad = await ciudades_collection.find_one({"_id": ciudad_id})
        if ciudad:
            ciudad["_id"] = str(ciudad["_id"])
            return ciudad
        return None
    except Exception as e:
        print(f"Error al obtener ciudad: {e}")
        return None

# ==============================================
# Funciones para Paquetes
# ==============================================
async def listar_paquetes() -> List[dict]:
    try:
        paquetes = await paquetes_collection.find().to_list(length=100)
        for paquete in paquetes:
            paquete["_id"] = str(paquete["_id"])  # Convertir ObjectId a string si es necesario
        return paquetes
    except Exception as e:
        print(f"Error al obtener paquetes: {e}")
        return []
    
async def obtener_paquete(paquete_id: str) -> Optional[dict]:
    try:
        paquete = await paquetes_collection.find_one({"_id": paquete_id})
        if paquete:
            paquete["_id"] = str(paquete["_id"])
            return paquete
        return None
    except Exception as e:
        print(f"Error al obtener paquete: {e}")
        return None

# ==============================================
# Rutas principales
# ==============================================
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("Index.html", {
        "request": request, 
        "active_page": "index"
    })

@app.get("/Camioneros", response_class=HTMLResponse)
async def mostrar_camioneros(request: Request):
    camioneros = await listar_camioneros()
    camiones = await listar_camiones()
    cuidades = await listar_ciudades()
    return templates.TemplateResponse("Camioneros.html", {
        "request": request,
        "active_page": "Camioneros",
        "Camioneros": camioneros,
        "Camiones": camiones,
        "poblaciones": cuidades
    })

@app.get("/Camiones", response_class=HTMLResponse)
async def mostrar_camiones(request: Request):
    camiones = await listar_camiones()
    camioneros = await camioneros_collection.find().to_list(length=100)
    return templates.TemplateResponse("Camiones.html", {
        "request": request,
        "active_page": "Camiones",
        "Camiones": camiones,
        "Camioneros": camioneros
    })

@app.get("/Ciudades", response_class=HTMLResponse)
async def mostrar_ciudades(request: Request):
    ciudades = await listar_ciudades()
    return templates.TemplateResponse("Ciudades.html", {
        "request": request,
        "active_page": "Ciudades",
        "Ciudades": ciudades
    })

@app.get("/Paquetes", response_class=HTMLResponse)
async def mostrar_paquetes(request: Request):
    # Obtener datos crudos de las colecciones
    paquetes = await listar_paquetes()
    ciudades = await listar_ciudades()
    camioneros = await listar_camioneros()
    
    # Crear diccionario para mapear IDs de ciudades a sus nombres
    ciudades_dict = {ciudad['_id']: ciudad['nombre'] for ciudad in ciudades}
    
    # Formatear los paquetes
    paquetes_formateados = []
    for paquete in paquetes:
        paquetes_formateados.append({
            "_id": paquete["_id"],
            "descripcion": paquete.get("descripcion", ""),
            "destino": ciudades_dict.get(paquete.get("ciudad_destino", ""), ""),  # Mostrar nombre
            "dir_destinatario": paquete.get("dir_destinatario", ""),
            "camionero_asignado": paquete.get("camionero_asignado", ""),
            "ciudad_destino": paquete.get("ciudad_destino", "")  # Mostrar ID
        })
    
    return templates.TemplateResponse("Paquetes.html", {
        "request": request,
        "active_page": "Paquetes",
        "Paquetes": paquetes_formateados,
        "Ciudades": ciudades,
        "Camioneros": camioneros
    })
# ==============================================
# API Endpoints para AJAX
# ==============================================
@app.get("/api/camiones")
async def obtener_camiones_api():
    camiones = await listar_camiones()
    return camiones

@app.get("/api/camioneros")
async def obtener_camioneros_api():
    camioneros = await listar_camioneros()
    return camioneros

@app.get("/api/ciudades")
async def obtener_ciudades_api():
    ciudades = await listar_ciudades()
    return ciudades

# ==============================================
# CRUD para Camioneros
# ==============================================
@app.post("/camioneros/agregar")
async def agregar_camionero(rfc: str = Form(...), nombre: str = Form(...), telefono: str = Form(...), direccion: str = Form(...), salario: float = Form(...), poblacion: str = Form(...), camiones: List[str] = Form([])):
    if await camioneros_collection.find_one({"_id": rfc}):
        raise HTTPException(status_code=400, detail="El RFC ya existe")

    nuevo_camionero = {
        "_id": rfc,
        "nombre": nombre,
        "telefono": telefono,
        "direccion": direccion,
        "salario": salario,
        "poblacion": poblacion,
        "camiones_asignados": camiones
    }
    await camioneros_collection.insert_one(nuevo_camionero)

    for camion_id in camiones:
        await camiones_collection.update_one({"_id": camion_id}, {"$addToSet": {"conductores": rfc}})

    return RedirectResponse(url="/Camioneros", status_code=303)

@app.post("/camioneros/editar/{rfc}")
async def editar_camionero(rfc: str, nombre: str = Form(...), telefono: str = Form(...), direccion: str = Form(...), salario: float = Form(...), poblacion: str = Form(...), camiones: List[str] = Form([])):
    camionero_actual = await camioneros_collection.find_one({"_id": rfc})
    if not camionero_actual:
        raise HTTPException(status_code=404, detail="Camionero no encontrado")

    camiones_anteriores = camionero_actual.get("camiones_asignados", [])
    await camioneros_collection.update_one({"_id": rfc}, {"$set": {
        "nombre": nombre,
        "telefono": telefono,
        "direccion": direccion,
        "salario": salario,
        "poblacion": poblacion,
        "camiones_asignados": camiones
    }})

    camiones_a_agregar = [c for c in camiones if c not in camiones_anteriores]
    for camion_id in camiones_a_agregar:
        await camiones_collection.update_one({"_id": camion_id}, {"$addToSet": {"conductores": rfc}})

    camiones_a_quitar = [c for c in camiones_anteriores if c not in camiones]
    for camion_id in camiones_a_quitar:
        await camiones_collection.update_one({"_id": camion_id}, {"$pull": {"conductores": rfc}})

    return RedirectResponse(url="/Camioneros", status_code=303)

@app.get("/camioneros/eliminar/{rfc}")
async def eliminar_camionero(rfc: str):
    paquetes_count = await paquetes_collection.count_documents({"camionero_asignado": rfc})
    if paquetes_count > 0:
        raise HTTPException(status_code=400, detail="No se puede eliminar el camionero porque tiene paquetes asignados")

    await camiones_collection.update_many({"conductores": rfc}, {"$pull": {"conductores": rfc}})
    result = await camioneros_collection.delete_one({"_id": rfc})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Camionero no encontrado")

    return RedirectResponse(url="/Camioneros", status_code=303)


# ==============================================
# CRUD para Camiones
# ==============================================
@app.post("/camiones/agregar")
async def agregar_camion(
    placa: str = Form(...),
    modelo: str = Form(...),
    tipo: str = Form(...),
    potencia: str = Form(...),
    conductores: List[str] = Form([])
):
    try:
        # Verificar si la placa ya existe
        if await camiones_collection.find_one({"placa": placa}):
            raise HTTPException(status_code=400, detail="La placa ya existe")
        
        nuevo_camion = {
            "placa": placa,
            "modelo": modelo,
            "tipo": tipo,
            "potencia": potencia,
            "conductores": conductores
        }
        
        await camiones_collection.insert_one(nuevo_camion)
        
        # Actualizar camioneros con este camión
        for rfc in conductores:
            await camioneros_collection.update_one(
                {"_id": rfc},
                {"$addToSet": {"camiones_asignados": str(nuevo_camion["_id"])}}
            )
        
        return RedirectResponse(url="/Camiones", status_code=303)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al agregar camión: {str(e)}")

@app.post("/camiones/editar/{placa}")  # Usamos 'placa' como parámetro en lugar de 'camion_id'
async def editar_camion(
    placa: str,  # La placa es el _id
    modelo: str = Form(...),
    tipo: str = Form(...),
    potencia: str = Form(...),
    conductores: List[str] = Form([])
):
    try:
        # Buscar el camión por su placa (que es el _id)
        camion_actual = await camiones_collection.find_one({"_id": placa})
        if not camion_actual:
            raise HTTPException(status_code=404, detail="Camión no encontrado")

        # Actualizar el camión usando la placa como _id
        await camiones_collection.update_one(
            {"_id": placa},  # Filtramos por la placa (que es el _id)
            {"$set": {
                "modelo": modelo,
                "tipo": tipo,
                "potencia": potencia,
                "conductores": conductores
            }}
        )

        # Actualizar conductores (código existente)
        conductores_anteriores = camion_actual.get("conductores", [])
        conductores_a_agregar = [c for c in conductores if c not in conductores_anteriores]
        for rfc in conductores_a_agregar:
            await camioneros_collection.update_one(
                {"_id": rfc},
                {"$addToSet": {"camiones_asignados": placa}}  # Usamos la placa como referencia
            )

        conductores_a_quitar = [c for c in conductores_anteriores if c not in conductores]
        for rfc in conductores_a_quitar:
            await camioneros_collection.update_one(
                {"_id": rfc},
                {"$pull": {"camiones_asignados": placa}}  # Usamos la placa como referencia
            )

        return RedirectResponse(url="/Camiones", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al editar camión: {str(e)}")

@app.get("/camiones/eliminar/{camion_id}")
async def eliminar_camion(camion_id: str):
    try:
        # Verificar si el camión tiene conductores asignados
        camion = await camiones_collection.find_one({"_id": ObjectId(camion_id)})
        if not camion:
            raise HTTPException(status_code=404, detail="Camión no encontrado")
        
        conductores = camion.get("conductores", [])
        if conductores:
            # Quitar este camión de los conductores que lo tengan asignado
            await camioneros_collection.update_many(
                {"_id": {"$in": conductores}},
                {"$pull": {"camiones_asignados": camion_id}}
            )
        
        # Eliminar el camión
        result = await camiones_collection.delete_one({"_id": ObjectId(camion_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Camión no encontrado")
            
        return RedirectResponse(url="/Camiones", status_code=303)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar camión: {str(e)}")
# CRUD para Ciudades
# ==============================================
@app.post("/ciudades/agregar")
async def agregar_ciudad(
    ciudad_id: str = Form(...),
    nombre: str = Form(...),
    apartado_postal: str = Form(...)
):
    try:
        # Verificar si la ciudad ya existe
        if await ciudades_collection.find_one({"_id": ciudad_id}):
            raise HTTPException(status_code=400, detail="La ciudad ya existe")
        
        nueva_ciudad = {
            "_id": ciudad_id,
            "nombre": nombre,
            "apartado_postal": apartado_postal
        }
        
        await ciudades_collection.insert_one(nueva_ciudad)
        return RedirectResponse(url="/Ciudades", status_code=303)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al agregar ciudad: {str(e)}")

@app.post("/ciudades/editar/{ciudad_id}")
async def editar_ciudad(
    ciudad_id: str,
    nombre: str = Form(...),
    apartado_postal: str = Form(...)
):
    try:
        # Verificar si la ciudad existe
        ciudad = await ciudades_collection.find_one({"_id": ciudad_id})
        if not ciudad:
            raise HTTPException(status_code=404, detail="Ciudad no encontrada")
        
        await ciudades_collection.update_one(
            {"_id": ciudad_id},
            {"$set": {
                "nombre": nombre,
                "apartado_postal": apartado_postal
            }}
        )
        
        return RedirectResponse(url="/Ciudades", status_code=303)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al editar ciudad: {str(e)}")

@app.get("/ciudades/eliminar/{ciudad_id}")
async def eliminar_ciudad(ciudad_id: str):
    try:
        # Verificar si hay paquetes que usan esta ciudad
        paquetes_count = await paquetes_collection.count_documents({"ciudad_destino": ciudad_id})
        if paquetes_count > 0:
            raise HTTPException(
                status_code=400,
                detail="No se puede eliminar la ciudad porque hay paquetes asociados"
            )
        
        result = await ciudades_collection.delete_one({"_id": ciudad_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Ciudad no encontrada")
            
        return RedirectResponse(url="/Ciudades", status_code=303)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar ciudad: {str(e)}")

# ==============================================
# CRUD para Paquetes
# ==============================================
@app.post("/paquetes/agregar")
async def agregar_paquete(
    paquete_id: str = Form(...),
    descripcion: str = Form(...),
    destino: str = Form(...),  # Nombre de la ciudad
    dir_destinatario: str = Form(...),
    camionero_asignado: str = Form(...),
    ciudad_destino: str = Form(...)  # ID de la ciudad
):
    try:
        # Verificar si el ID del paquete ya existe
        if await paquetes_collection.find_one({"_id": paquete_id}):
            raise HTTPException(status_code=400, detail="El ID del paquete ya existe")
        
        # Verificar que el camionero existe
        camionero = await camioneros_collection.find_one({"_id": camionero_asignado})
        if not camionero:
            raise HTTPException(status_code=400, detail="Camionero no encontrado")
        
        # Verificar que la ciudad existe
        ciudad = await ciudades_collection.find_one({"_id": ciudad_destino})
        if not ciudad:
            raise HTTPException(status_code=400, detail="Ciudad destino no encontrada")
        
        nuevo_paquete = {
            "_id": paquete_id,
            "descripcion": descripcion,
            "destino": destino,
            "dir_destinatario": dir_destinatario,
            "camionero_asignado": camionero_asignado,
            "ciudad_destino": ciudad_destino
        }
        
        await paquetes_collection.insert_one(nuevo_paquete)
        return RedirectResponse(url="/Paquetes", status_code=303)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al agregar paquete: {str(e)}")

@app.post("/paquetes/editar/{paquete_id}")
async def editar_paquete(
    paquete_id: str,
    descripcion: str = Form(...),
    destino: str = Form(...),  # Nombre de la ciudad
    dir_destinatario: str = Form(...),
    camionero_asignado: str = Form(...),
    ciudad_destino: str = Form(...)  # ID de la ciudad
):
    try:
        # Verificar que el paquete existe
        paquete = await paquetes_collection.find_one({"_id": paquete_id})
        if not paquete:
            raise HTTPException(status_code=404, detail="Paquete no encontrado")
        
        # Verificar que el camionero existe
        camionero = await camioneros_collection.find_one({"_id": camionero_asignado})
        if not camionero:
            raise HTTPException(status_code=400, detail="Camionero no encontrado")
        
        # Verificar que la ciudad existe
        ciudad = await ciudades_collection.find_one({"_id": ciudad_destino})
        if not ciudad:
            raise HTTPException(status_code=400, detail="Ciudad destino no encontrada")
        
        await paquetes_collection.update_one(
            {"_id": paquete_id},
            {"$set": {
                "descripcion": descripcion,
                "destino": destino,
                "dir_destinatario": dir_destinatario,
                "camionero_asignado": camionero_asignado,
                "ciudad_destino": ciudad_destino
            }}
        )
        
        return RedirectResponse(url="/Paquetes", status_code=303)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al editar paquete: {str(e)}")

@app.get("/paquetes/eliminar/{paquete_id}")
async def eliminar_paquete(paquete_id: str):
    try:
        result = await paquetes_collection.delete_one({"_id": paquete_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Paquete no encontrado")
            
        return RedirectResponse(url="/Paquetes", status_code=303)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar paquete: {str(e)}")

# ==============================================
# Consultas
# ==============================================
@app.get("/consultas", response_class=HTMLResponse)
async def mostrar_consultas(request: Request):
    return templates.TemplateResponse("Consultas.html", {
        "request": request,
        "active_page": "consultas"
    })

@app.get("/consultas/camioneros-paquetes")
async def consulta_camioneros_paquetes():
    """
    CONSULTA 1: Muestra los camioneros y la cantidad de paquetes que ha llevado
    """
    try:
        pipeline = [
            {
                "$group": {
                    "_id": "$camionero_asignado",
                    "cantidad_paquetes": {"$sum": 1}
                }
            },
            {
                "$lookup": {
                    "from": "camionero",
                    "localField": "_id",
                    "foreignField": "_id",
                    "as": "camionero_info"
                }
            },
            {
                "$unwind": "$camionero_info"
            },
            {
                "$project": {
                    "rfc": "$_id",
                    "nombre": "$camionero_info.nombre",
                    "cantidad_paquetes": 1,
                    "_id": 0
                }
            },
            {
                "$sort": {"cantidad_paquetes": -1}
            }
        ]
        
        resultados = await paquetes_collection.aggregate(pipeline).to_list(length=100)
        return JSONResponse(resultados)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en consulta camioneros-paquetes: {str(e)}")
    

@app.get("/consultas/camioneros-camiones")
async def consulta_camioneros_camiones():
    """
    CONSULTA 2: Muestra los camioneros y los modelos de camiones que conducen
    """
    try:
        camioneros = await camioneros_collection.find().to_list(length=100)
        
        resultados = []
        for camionero in camioneros:
            modelos_camiones = []
            if "camiones_asignados" in camionero:
                for camion_id in camionero["camiones_asignados"]:
                    try:
                        if ObjectId.is_valid(camion_id):
                            camion = await camiones_collection.find_one({"_id": ObjectId(camion_id)})
                        else:
                            camion = await camiones_collection.find_one({"_id": camion_id})
                        
                        if camion:
                            modelo = camion.get("modelo") or camion.get("Modelo") or camion.get("tipo") or "Modelo no especificado"
                            modelos_camiones.append(modelo)
                        else:
                            modelos_camiones.append(f"Camion-ID: {camion_id} (no existe)")
                    except Exception as e:
                        modelos_camiones.append(f"Error: {str(e)}")
            
            # Unir los modelos en un string
            modelos_str = ", ".join(modelos_camiones) if modelos_camiones else "Ninguno"
            
            resultados.append({
                'RFC': camionero['_id'],
                'Nombre': camionero.get('nombre', 'Sin nombre'),
                'Cantidad de Camiones': len(camionero.get('camiones_asignados', [])),
                'Modelos de Camiones': modelos_str
            })
        
        return JSONResponse(resultados)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en consulta camioneros-camiones: {str(e)}")

@app.get("/consultas/detalle-entregas")
async def consulta_detalle_entregas():
    """
    CONSULTA 3: Muestra nombre del camionero, placa del camión, descripción de paquete,
    dirección del destinatario y nombre de la ciudad destino
    """
    try:
        pipeline = [
            {
                "$lookup": {
                    "from": "camionero",
                    "localField": "camionero_asignado",
                    "foreignField": "_id",
                    "as": "camionero_info"
                }
            },
            {
                "$unwind": "$camionero_info"
            },
            {
                "$lookup": {
                    "from": "ciudad",
                    "localField": "ciudad_destino",
                    "foreignField": "_id",
                    "as": "ciudad_info"
                }
            },
            {
                "$unwind": "$ciudad_info"
            },
            {
                "$lookup": {
                    "from": "camion",
                    "let": {"camionero_rfc": "$camionero_asignado"},
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$in": ["$$camionero_rfc", "$conductores"]
                                }
                            }
                        }
                    ],
                    "as": "camion_info"
                }
            },
            {
                "$unwind": {
                    "path": "$camion_info",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "nombre_camionero": "$camionero_info.nombre",
                    "placa_camion": "$camion_info.placa",
                    "descripcion_paquete": "$descripcion",
                    "direccion_destinatario": "$dir_destinatario",
                    "ciudad_destino": "$ciudad_info.nombre"
                }
            }
        ]
        
        resultados = await paquetes_collection.aggregate(pipeline).to_list(length=100)
        return JSONResponse(resultados)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en consulta detalle-entregas: {str(e)}")

@app.get("/consultas/ciudades-sin-paquetes")
async def consulta_ciudades_sin_paquetes():
    """
    CONSULTA 4: Listado de ciudades a donde no han llegado paquetes
    """
    try:
        # Obtener todas las ciudades
        todas_ciudades = await ciudades_collection.find().to_list(length=100)
        
        # Obtener las ciudades que tienen paquetes
        pipeline = [
            {
                "$group": {
                    "_id": "$ciudad_destino"
                }
            }
        ]
        ciudades_con_paquetes = await paquetes_collection.aggregate(pipeline).to_list(length=100)
        ciudades_con_paquetes_ids = [c["_id"] for c in ciudades_con_paquetes]
        
        # Filtrar ciudades que no están en la lista de ciudades con paquetes
        ciudades_sin_paquetes = [
            ciudad for ciudad in todas_ciudades 
            if ciudad["_id"] not in ciudades_con_paquetes_ids
        ]
        
        # Convertir ObjectId a string si es necesario
        for ciudad in ciudades_sin_paquetes:
            ciudad["_id"] = str(ciudad["_id"])
        
        return JSONResponse( ciudades_sin_paquetes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en consulta ciudades-sin-paquetes: {str(e)}")

# ==============================================
# Iniciar la aplicación
# ==============================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001, reload=True)