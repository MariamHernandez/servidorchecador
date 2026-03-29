from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

MONGO_URI = "mongodb+srv://desconexionparcial:LwryVX9pbCjdM8ao@cluster0.7rjoqap.mongodb.net/Registro_Alu?retryWrites=true&w=majority"

def conectar_mongo():
    try:
        cliente = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=5000
        )

        cliente.admin.command("ping")

        return cliente, "✅ Conexión exitosa a MongoDB"

    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        return None, f"❌ Error de conexión: {str(e)}"

    except Exception as e:
        return None, f"❌ Error inesperado: {str(e)}"
    
def obtener_trabajadores(cliente):
    db = cliente["Registro_Alu"]
    return list(db.trabajadores.find({}))

def obtener_sede_por_id(cliente, sede_id):
    db = cliente["Registro_Alu"]
    return db.sedes.find_one({"id": sede_id}, {"_id": 0}
    )

def obtener_sedes(cliente):
    db = cliente["Registro_Alu"]
    return list(
        db.sedes.find({}, {"_id": 0, "id": 1, "nombre": 1, "password": 1})
    )