# mongo_service.py
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

#MONGO_URI = "mongodb+srv://desconexionparcial:LwryVX9pbCjdM8ao@cluster0.7rjoqap.mongodb.net/Registro_Alu?retryWrites=true&w=majority"
MONGO_URI= "mongodb+srv://dpalupratic_db_user:24AT1qpZgQAO2Hyt@dbprod.l0mixcb.mongodb.net/Registro_Alu?retryWrites=true&w=majority"



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
    Regresa los trabajadores activos que deben existir
    en el checador de la sede actual.

    Un trabajador pertenece a la sede cuando:

    1. Su sede principal coincide con la sede actual.
    2. Su campo legacy 'sede' coincide con la sede actual.
    3. La sede actual aparece dentro de sedesForaneas.

    Esto permite que un trabajador pueda existir en varios
    checadores sin dejar de tener una sola sede principal.
    """

    db = cliente["Registro_Alu"]
    coleccion = db.trabajadores

    # ==========================================================
    # NORMALIZAR ID DE SEDE
    # ==========================================================
    # Dependiendo de cómo se haya guardado la configuración,
    # sede_id podría llegar como int o como string.
    # Buscamos ambas variantes para evitar problemas.
    valores_sede = []

    if sede_id is not None:
        valores_sede.append(sede_id)

    try:
        sede_num = int(sede_id)

        if sede_num not in valores_sede:
            valores_sede.append(sede_num)

        sede_str = str(sede_num)

        if sede_str not in valores_sede:
            valores_sede.append(sede_str)

    except (TypeError, ValueError):
        pass

    # ==========================================================
    # FILTRO DE TRABAJADORES
    # ==========================================================
    filtro = {
        "estado": {"$ne": "inactivo"},

        "$or": [

            # --------------------------------------------------
            # COMPATIBILIDAD CON EL CAMPO ANTERIOR
            # --------------------------------------------------
            {
                "sede": {
                    "$in": valores_sede
                }
            },

            # --------------------------------------------------
            # SEDE PRINCIPAL
            # --------------------------------------------------
            {
                "sedePrincipal": {
                    "$in": valores_sede
                }
            },

            # --------------------------------------------------
            # SEDES FORANEAS
            # MongoDB busca automáticamente dentro del array.
            # --------------------------------------------------
            {
                "sedesForaneas": {
                    "$in": valores_sede
                }
            }
        ]
    }

    # ==========================================================
    # CAMPOS NECESARIOS
    # ==========================================================
    proyeccion = {
        "_id": 1,
        "nombre": 1,
        "apellido": 1,
        "id_checador": 1,

        "sede": 1,
        "sedePrincipal": 1,
        "sedesForaneas": 1
    }

    trabajadores = list(
        coleccion.find(
            filtro,
            proyeccion
        )
    )

    # ==========================================================
    # NORMALIZAR RESULTADO
    # ==========================================================
    resultado = []

    for t in trabajadores:

        id_checador = str(
            t.get("id_checador", "")
        ).strip()

        # Sin ID de checador no podemos enviarlo al dispositivo.
        if not id_checador:
            continue

        nombre = (
            t.get("nombre", "") or ""
        ).strip()

        apellido = (
            t.get("apellido", "") or ""
        ).strip()

        nombre_completo = f"{nombre} {apellido}".strip()

        resultado.append({
            "_id": str(t.get("_id")),

            "id_checador": id_checador,

            "nombre": nombre_completo or id_checador,

            "sede": t.get("sede"),

            "sedePrincipal": t.get("sedePrincipal"),

            "sedesForaneas": t.get(
                "sedesForaneas",
                []
            )
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
        # Se envia una copia para evitar que PyMongo
        # agregue el _id ObjectId al documento original
            coleccion.insert_one(dict(doc))
            insertados += 1

    return {
        "insertados": insertados,
        "actualizados": actualizados,
        "total": len(documentos)
    }