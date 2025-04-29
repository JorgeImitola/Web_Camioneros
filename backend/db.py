from motor.motor_asyncio import AsyncIOMotorClient

# Conectar al servidor de MongoDB
client = AsyncIOMotorClient("mongodb://localhost:27017")

# Acceder a la base de datos correctamente por su nombre
db = client["Gestion_paquetes"]

# Acceder a las colecciones
camiones_collection = db["camion"]
paquetes_collection = db["paquete"]
camioneros_collection = db["camionero"]
ciudades_collection = db["ciudad"]