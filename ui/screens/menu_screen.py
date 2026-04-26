from tkinter import ttk
import ttkbootstrap as tb
import sys
from pathlib import Path
from ui.styles.theme import configure_app_style

def obtener_ruta_recurso(rel_path):
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / rel_path
    return Path(rel_path)

class MenuScreen:
    def __init__(
        self,
        on_sincronizacion_manual_callback,
        on_iniciar_auto_sync_callback,
        on_detener_auto_sync_callback,
        on_limpiar_callback,
        on_reconfigurar_callback,
        on_salir_callback,
        config_data=None
    ):
        self.window = tb.Window(themename="cosmo")
        self.window.title("Menú principal - Alu Asistencias")
        self.window.geometry("860x620")
        self.window.resizable(False, False)

        icon_path = obtener_ruta_recurso("icono.ico")
        if icon_path.exists():
            self.window.iconbitmap(str(icon_path))

        configure_app_style(self.window)

        self.on_sincronizacion_manual_callback = on_sincronizacion_manual_callback
        self.on_iniciar_auto_sync_callback = on_iniciar_auto_sync_callback
        self.on_detener_auto_sync_callback = on_detener_auto_sync_callback
        self.on_reconfigurar_callback = on_reconfigurar_callback
        self.on_salir_callback = on_salir_callback
        self.config_data = config_data or {}
        self.on_limpiar_callback = on_limpiar_callback

        self._build_ui()

    def _build_ui(self):
        card = tb.Frame(self.window, padding=(28, 24), style="Card.TFrame")
        card.pack(expand=True, padx=28, pady=28, fill="both")

        titulo = tb.Label(
            card,
            text="Menú principal · Alu Asistencias",
            style="Title.TLabel"
        )
        titulo.pack(pady=(6, 4))

        subtitulo = tb.Label(
            card,
            text="Servidor local listo para operar",
            style="Subtitle.TLabel"
        )
        subtitulo.pack(pady=(0, 18))

        info_frame = tb.Frame(card, style="Card.TFrame")
        info_frame.pack(pady=(0, 18), fill="x")

        sede = self.config_data.get("nombre_sede", "No disponible")
        sede_id = self.config_data.get("sede", "N/D")
        ip = self.config_data.get("checador_ip", "N/D")

        tb.Label(
            info_frame,
            text=f"📍 Sede: {sede}",
            style="Muted.TLabel"
        ).pack(anchor="w", pady=2)

        tb.Label(
            info_frame,
            text=f"🆔 ID sede: {sede_id}",
            style="Muted.TLabel"
        ).pack(anchor="w", pady=2)

        tb.Label(
            info_frame,
            text=f"📡 Checador: {ip}",
            style="Muted.TLabel"
        ).pack(anchor="w", pady=2)

        acciones = tb.Frame(card, style="Card.TFrame")
        acciones.pack(pady=(10, 0))

        self.btn_sync_manual = tb.Button(
            acciones,
            text="🔄 Sincronización manual",
            bootstyle="primary",
            command=self.on_sincronizacion_manual_callback
        )
        self.btn_sync_manual.grid(row=0, column=0, padx=10, pady=10, ipadx=10, ipady=6)

        self.btn_auto_on = tb.Button(
            acciones,
            text="▶ Iniciar auto sync",
            bootstyle="success",
            command=self.on_iniciar_auto_sync_callback
        )
        self.btn_auto_on.grid(row=0, column=1, padx=10, pady=10, ipadx=10, ipady=6)

        self.btn_auto_off = tb.Button(
            acciones,
            text="⏹ Detener auto sync",
            bootstyle="info",
            command=self.on_detener_auto_sync_callback
        )
        self.btn_auto_off.grid(row=0, column=2, padx=10, pady=10, ipadx=10, ipady=6)

        self.btn_reconfigurar = tb.Button(
            acciones,
            text="⚙️ Reconfigurar",
            bootstyle="warning",
            command=self.on_reconfigurar_callback
        )
        
        self.btn_reconfigurar.grid(row=1, column=0, padx=10, pady=10, ipadx=10, ipady=6)

        self.btn_limpiar = tb.Button(
            acciones,
            text="🧹 Limpiar checador",
            bootstyle="secondary",
            command=self.on_limpiar_callback
        )
        self.btn_limpiar.grid(row=1, column=2, padx=10, pady=10, ipadx=10, ipady=6)

        self.btn_salir = tb.Button(
            acciones,
            text="✖ Salir",
            bootstyle="danger-outline",
            command=self.on_salir_callback
        )
        self.btn_salir.grid(row=1, column=1, padx=10, pady=10, ipadx=10, ipady=6)

        estado_auto_frame = tb.Frame(card, style="Card.TFrame")
        estado_auto_frame.pack(pady=(18, 6), fill="x")

        self.auto_sync_label = tb.Label(
            estado_auto_frame,
            text="Auto sync: desactivada",
            style="Muted.TLabel"
        )
        self.auto_sync_label.pack(anchor="w", pady=2)

        self.proxima_sync_label = tb.Label(
            estado_auto_frame,
            text="Próxima ejecución: no programada",
            style="Muted.TLabel"
        )
        self.proxima_sync_label.pack(anchor="w", pady=2)

        self.progress = ttk.Progressbar(
            card,
            mode="indeterminate",
            length=100
        )
        self.progress.pack(fill="x", pady=(12, 8))
        self.progress.pack_forget()

        self.estado_label = tb.Label(
            card,
            text="Estado: Sistema listo",
            style="Success.TLabel"
        )
        self.estado_label.pack(pady=(12, 0))

    def set_estado(self, texto, tipo="muted"):
        estilos = {
            "success": "Success.TLabel",
            "danger": "Danger.TLabel",
            "muted": "Muted.TLabel"
        }
        self.estado_label.config(text=texto, style=estilos.get(tipo, "Muted.TLabel"))

    def set_estado_auto_sync(self, texto, tipo="muted"):
        estilos = {
            "success": "Success.TLabel",
            "danger": "Danger.TLabel",
            "muted": "Muted.TLabel"
        }
        self.auto_sync_label.config(text=texto, style=estilos.get(tipo, "Muted.TLabel"))

    def set_proxima_sync(self, texto, tipo="muted"):
        estilos = {
            "success": "Success.TLabel",
            "danger": "Danger.TLabel",
            "muted": "Muted.TLabel"
        }
        self.proxima_sync_label.config(text=texto, style=estilos.get(tipo, "Muted.TLabel"))

    def mostrar_progreso(self):
        self.progress.pack(fill="x", pady=(12, 8))
        self.progress.start(10)

    def ocultar_progreso(self):
        self.progress.stop()
        self.progress.pack_forget()

    def iniciar(self):
        self.window.mainloop()