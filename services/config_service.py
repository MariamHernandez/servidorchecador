import json
import os
from datetime import datetime


CONFIG_FILE = "configuracion_temporal.json"


def guardar_configuracion(sede_id, nombre_sede, checador_ip):
    data = {
        "sede": sede_id,
        "nombre_sede": nombre_sede,
        "checador_ip": checador_ip,
        "setup_done": True,
        "ts": datetime.now().isoformat()
    }

    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print("✅ Configuración guardada correctamente")
        return True

    except Exception as e:
        print(f"❌ Error al guardar configuración: {e}")
        return False

def cargar_configuracion():
    if not os.path.exists(CONFIG_FILE):
        return None

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None
    
def eliminar_configuracion():
    if not os.path.exists(CONFIG_FILE):
        return True

    try:
        os.remove(CONFIG_FILE)
        print("✅ Configuración eliminada correctamente")
        return True
    except Exception as e:
        print(f"❌ Error al eliminar configuración: {e}")
        return False
