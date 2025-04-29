from fastapi import FastAPI
import uvicorn
from routes.camion import router as camion_router
from routes.ciudad import router as ciudad_router
from routes.paquete import router as paquete_router
from routes.camionero import router as camionero_router

app = FastAPI(title="Gestión de Paquetes API", version="1.0.0")
@app.get("/")
def welcome():
    return {"message": "Welcome to the FastAPI application!"}

app.include_router(camion_router, prefix="/api")  # Rutas relacionadas con clientes
app.include_router(ciudad_router, prefix="/api")  # Rutas relacionadas con proveedores
app.include_router(paquete_router, prefix="/api")  # Rutas relacionadas con productos
app.include_router(camionero_router, prefix="/api")  # Rutas relacionadas con compras


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)