import os
import json
from datetime import datetime
from pathlib import Path

from utils.constants import RESPALDOS_DIR


def guardar_respaldo_manual(documentos, sede=None, checador_ip=None, resumen=None, carpeta_base=None):
    """
    Guarda un respaldo JSON local de una sincronizacion manual.

    Parametros:
    - documentos: lista de documentos consolidados
    - sede: identificador de la sede
    - checador_ip: IP del checador
    - resumen: resultado del guardado en Mongo
    - carpeta_base: carpeta raiz de respaldos (opcional)

    Retorna:
    - ruta_archivo: ruta completa del JSON generado
    """

    ahora = datetime.now()
    fecha_carpeta = ahora.strftime("%Y-%m-%d")

    if carpeta_base is None:
        carpeta_base = RESPALDOS_DIR / "manual"
    else:
        carpeta_base = Path(carpeta_base)

    carpeta_destino = carpeta_base / fecha_carpeta
    carpeta_destino.mkdir(parents=True, exist_ok=True)

    ruta_archivo = carpeta_destino / "ultimo_respaldo.json"

    contenido = {
        "tipo": "sincronizacion_manual",
        "generado": ahora.isoformat(),
        "sede": sede,
        "checador_ip": checador_ip,
        "total_documentos": len(documentos),
        "resumen_mongo": resumen,
        "documentos": documentos
    }

    with open(ruta_archivo, "w", encoding="utf-8") as archivo:
        json.dump(contenido, archivo, ensure_ascii=False, indent=4)

    return str(ruta_archivo)