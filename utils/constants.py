import os
from pathlib import Path


def _obtener_documents_dir():
    home = Path.home()

    candidates = [
        home / "Documents",
        home / "OneDrive" / "Documents",
        home / "OneDrive" / "Documentos",
        home / "Documentos",
    ]

    for path in candidates:
        if path.exists():
            return path

    return home


def _obtener_localappdata_real():
    home = Path.home()

    candidates = [
        Path(os.environ.get("LOCALAPPDATA", "")) if os.environ.get("LOCALAPPDATA") else None,
        home / "AppData" / "Local",
    ]

    for path in candidates:
        if path and path.exists():
            return path

    return home / "AppData" / "Local"


LOCAL_APPDATA = _obtener_localappdata_real()
APPDATA_DIR = LOCAL_APPDATA / "AluAsistencias"

DOCUMENTOS_DIR = _obtener_documents_dir() / "Alu Asistencias"
RESPALDOS_DIR = DOCUMENTOS_DIR / "respaldos"

CONFIG_PATH = APPDATA_DIR / "configuracion_temporal.json"

APPDATA_DIR.mkdir(parents=True, exist_ok=True)
DOCUMENTOS_DIR.mkdir(parents=True, exist_ok=True)
RESPALDOS_DIR.mkdir(parents=True, exist_ok=True)