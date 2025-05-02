from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from routes.camionero import listar_camioneros, router as camioneros_router
from routes.camion import listar_camiones, router as camiones_router
from routes.ciudad import listar_ciudades, router as ciudades_router
from routes.paquete import listar_paquetes,router as paquetes_router
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Incluir routers
app.include_router(camioneros_router, prefix="/camioneros")
app.include_router(camiones_router, prefix="/camiones")
app.include_router(ciudades_router, prefix="/ciudades")
app.include_router(paquetes_router, prefix="/paquetes")



# ==============================================
# Rutas principales
# ==============================================
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("Index.html", {
        "request": request, 
        "active_page": "index"
        })
    
@app.get("/Camioneros", response_class=HTMLResponse )
async def read_camioneros(request: Request):
    Camioneros = await listar_camioneros()
    return templates.TemplateResponse("Camioneros.html", {
        "request": request,
        "active_page": "Camioneros",
        "Camioneros": Camioneros
    })
    
@app.get("/Camiones", response_class=HTMLResponse)
async def mostrar_camiones(request: Request):
    camiones = await listar_camiones()
    formatted_camiones = []
    for camion in camiones:
        formatted_camiones.append({
            "_id": camion["_id"],
            "placa": camion.get("placa", ""),
            "modelo": camion.get("modelo", ""),
            "tipo": camion.get("tipo", ""),
            "potencia": camion.get("potencia", ""),
            "conductores": ", ".join(camion.get("conductores", [])) if camion.get("conductores") else "Ninguno"
        })
    return templates.TemplateResponse("Camiones.html", {
        "request": request,
        "Camiones": formatted_camiones
    })

@app.get("/Ciudades", response_class=HTMLResponse )
async def read_camioneros(request: Request):
    Ciudades = await listar_ciudades()
    return templates.TemplateResponse("Ciudades.html", {
        "request": request,
        "active_page": "Ciudades",
        "Ciudades": Ciudades
    })
    
@app.get("/Paquetes", response_class=HTMLResponse )
async def read_camioneros(request: Request):
    Paquetes = await listar_paquetes()
    return templates.TemplateResponse("Paquetes.html", {
        "request": request,
        "active_page": "Paquetes",
        "Paquetes": Paquetes
    })

# ==============================================
# Otras rutas
# ==============================================
@app.get("/consultas", response_class=HTMLResponse)
async def read_consultas(request: Request):
    return templates.TemplateResponse("Consultas.html", {
        "request": request, 
        "active_page": "consultas"})


# ==============================================
# Iniciar la aplicación
# ==============================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001, reload=True)