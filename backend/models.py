from pydantic import BaseModel,Field
from typing import List, Optional
from datetime import datetime

#CAMION
class CamionBase(BaseModel):
    id: str=Field(alias="_id")
    modelo: str
    tipo: str
    potencia: str
    conductores: list[str] 
    class Config:
        populate_by_name = True  # Esto permite usar .id pero guardar como _id


class CamionUpdate(BaseModel):
    modelo: Optional[str] = None
    tipo: Optional[str] = None
    potencia: Optional[str] = None
    conductores: Optional[List[str]] = None

#CAMIONERO
class CamioneroBase(BaseModel):
    id: str=Field(alias="_id")
    nombre: str
    telefono: str
    direccion: str
    salario: float
    poblacion: Optional[str] = None
    camiones: List[str] = Field(default=[], description="Lista de placas de camiones asignados")

class CamioneroUpdate(BaseModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    salario: Optional[float] = None
    poblacion: Optional[str] = None

#CIUDAD
class CiudadBase(BaseModel):
    id: str=Field(alias="_id")
    nombre: str
    apartado_postal: str


class CiudadUpdate(BaseModel):
    nombre: Optional[str] = None
    apartado_postal: Optional[str] = None


# PAQUETE
class PaqueteBase(BaseModel):
    id: str=Field(alias="_id")
    descripcion: str
    destino: str
    dir_destinatario: str
    camionero_asignado: str
    ciudad_destino: str
    ciudad_destino: str
 #   fecha_entrega: Optional[datetime] = None

class PaqueteUpdate(BaseModel):
    descripcion: Optional[str] = None
    destino: Optional[str] = None
    dir_destinatario: Optional[str] = None
    camionero_asignado: Optional[str] = None
    ciudad_destino: Optional[str] = None
    codigo_ciudad: Optional[str] = None
  #  fecha_entrega: Optional[datetime] = None