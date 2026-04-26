import sys
import subprocess
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
MAIN_PATH = BASE_DIR / "main.py"


def _reiniciar_proceso():
    if getattr(sys, "frozen", False):
        subprocess.Popen([sys.executable])
    else:
        subprocess.Popen([sys.executable, str(MAIN_PATH)])

    sys.exit()


def reiniciar_aplicacion():
    _reiniciar_proceso()


def ir_a_menu():
    _reiniciar_proceso()