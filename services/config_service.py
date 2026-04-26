import json
import os
from datetime import datetime

from utils.constants import CONFIG_PATH


def guardar_configuracion(sede_id, nombre_sede, checador_ip):
    data = {
        "sede": sede_id,
        "nombre_sede": nombre_sede,
        "checador_ip": checador_ip,
        "setup_done": True,
        "ts": datetime.now().isoformat()
    }

    try:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print(f"[OK] Configuracion guardada correctamente en: {CONFIG_PATH}")
        return True

    except Exception as e:
        print(f"[ERROR] Error al guardar configuración: {e}")
        return False


def cargar_configuracion():
    if not os.path.exists(CONFIG_PATH):
        return None

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Error al cargar configuración: {e}")
        return None


def eliminar_configuracion():
    if not os.path.exists(CONFIG_PATH):
        return True

    try:
        os.remove(CONFIG_PATH)
        print(f"[OK] Configuración eliminada correctamente de: {CONFIG_PATH}")
        return True
    except Exception as e:
        print(f"[ERROR] Error al eliminar configuración: {e}")
        return False