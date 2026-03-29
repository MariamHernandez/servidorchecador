from tkinter import messagebox

from ui.screens.menu_screen import MenuScreen
from services.config_service import cargar_configuracion, eliminar_configuracion
from services.navigation_service import reiniciar_aplicacion


class MenuController:
    def __init__(self):
        self.config_data = cargar_configuracion() or {}

        self.screen = MenuScreen(
            on_sincronizacion_manual_callback=self.sincronizacion_manual,
            on_reconfigurar_callback=self.reconfigurar,
            on_salir_callback=self.salir,
            config_data=self.config_data
        )

        self.screen.window.protocol("WM_DELETE_WINDOW", self.salir)

    def iniciar(self):
        self.screen.iniciar()

    def sincronizacion_manual(self):
        self.screen.set_estado("Estado: ⏳ Sincronización manual aún no implementada", "muted")
        print("Próximo paso: implementar sincronización manual")

    def reconfigurar(self):
        confirmar = messagebox.askyesno(
            "Reconfigurar",
            "Se eliminará la configuración actual y el sistema volverá al inicio.\n\n¿Deseas continuar?"
        )

        if not confirmar:
            return

        ok = eliminar_configuracion()

        if ok:
            self.screen.set_estado("Estado: ✅ Configuración eliminada. Reiniciando...", "success")
            self.screen.window.after(600, self._reiniciar)
        else:
            self.screen.set_estado("Estado: ❌ No se pudo eliminar la configuración", "danger")

    def _reiniciar(self):
        self.screen.window.destroy()
        reiniciar_aplicacion()

    def salir(self):
        self.screen.window.destroy()
