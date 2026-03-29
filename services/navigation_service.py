import os
import sys


def ir_a_menu():
    os.execl(sys.executable, sys.executable, "menu.py")


def reiniciar_aplicacion():
    os.execl(sys.executable, sys.executable, "main.py")
