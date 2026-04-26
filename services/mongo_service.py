from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

MONGO_URI = "mongodb+srv://desconexionparcial:LwryVX9pbCjdM8ao@cluster0.7rjoqap.mongodb.net/Registro_Alu?retryWrites=true&w=majority"
#MONGO_URI = "mongodb+srv://dpalupratic_db_user:24AT1qpZgQAO2Hyt@dbprod.l0mixcb.mongodb.net/"

def conectar_mongo():
    try:
        cliente = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=5000
        )

        cliente.admin.command("ping")

        return cliente, "Conexion exitosa a MongoDB"

    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        return None, f"Error de conexion: {str(e)}"

    except Exception as e:
        return None, f"Error inesperado: {str(e)}"
    
def obtener_trabajadores(cliente):
    db = cliente["Registro_Alu"]
    return list(db.trabajadores.find({}))

def obtener_sede_por_id(cliente, sede_id):
    db = cliente["Registro_Alu"]
    return db.sedes.find_one({"id": sede_id}, {"_id": 0}
    )

def obtener_trabajadores_activos_por_sede(cliente, sede_id):
    """
    Regresa trabajadores activos de la sede con datos útiles para sincronizar al checador.
    """
    db = cliente["Registro_Alu"]
    coleccion = db.trabajadores

    filtro = {
        "sede": sede_id,
        "estado": {"$ne": "inactivo"}
    }

    proyeccion = {
        "_id": 1,
        "nombre": 1,
        "apellido": 1,
        "id_checador": 1,
        "sede": 1
    }

    trabajadores = list(coleccion.find(filtro, proyeccion))

    resultado = []
    for t in trabajadores:
        id_checador = str(t.get("id_checador", "")).strip()
        if not id_checador:
            continue

        nombre = (t.get("nombre", "") or "").strip()
        apellido = (t.get("apellido", "") or "").strip()
        nombre_completo = f"{nombre} {apellido}".strip()

        resultado.append({
            "_id": str(t.get("_id")),
            "id_checador": id_checador,
            "nombre": nombre_completo or id_checador,
            "sede": t.get("sede")
        })

    return resultado

def obtener_sedes(cliente):
    db = cliente["Registro_Alu"]
    return list(
        db.sedes.find({}, {"_id": 0, "id": 1, "nombre": 1, "password": 1})
    )

def guardar_asistencias_consolidadas(cliente, documentos):
    """
    Inserta o actualiza asistencias consolidadas por:
    - trabajador
    - sede
    - fecha

    Retorna un resumen:
    {
        "insertados": X,
        "actualizados": Y,
        "total": Z
    }
    """
    db = cliente["Registro_Alu"]
    coleccion = db.asistencias

    insertados = 0
    actualizados = 0

    for doc in documentos:
        filtro = {
            "trabajador": doc["trabajador"],
            "sede": doc["sede"],
            "fecha": doc["fecha"]
        }

        existente = coleccion.find_one(filtro, {"_id": 1})

        if existente:
            coleccion.update_one(
                {"_id": existente["_id"]},
                {"$set": doc}
            )
            actualizados += 1
        else:
            coleccion.insert_one(doc)
            insertados += 1

    return {
        "insertados": insertados,
        "actualizados": actualizados,
        "total": len(documentos)
    }