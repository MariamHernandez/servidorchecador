import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk

from ui.styles.theme import configure_app_style


class InicioScreen:

    def __init__(self, on_iniciar_callback, on_salir_callback, on_cancelar_callback):
        self.window = tb.Window(themename="cosmo")
        self.window.title("Disboart - Alu Asistencias")
        self.window.geometry("860x520")
        self.window.resizable(False, False)

        configure_app_style(self.window)

        # Callbacks (los define el controller)
        self.on_iniciar_callback = on_iniciar_callback
        self.on_salir_callback = on_salir_callback
        self.on_cancelar_callback = on_cancelar_callback

        self._build_ui()

    # =============================
    # Construcción de UI
    # =============================
    def _build_ui(self):
        card = tb.Frame(self.window, padding=(28, 24), style="Card.TFrame")
        card.pack(expand=True, padx=28, pady=28)

        # Título
        self.titulo = tb.Label(
            card,
            text="🚀 Servidor Local · Alu Asistencias",
            style="Title.TLabel"
        )
        self.titulo.pack(pady=(6, 4))

        self.subtitulo = tb.Label(
            card,
            text="Sistema de asistencia empresarial",
            style="Subtitle.TLabel"
        )
        self.subtitulo.pack(pady=(0, 16))

        # Botones
        acciones = tb.Frame(card)
        acciones.pack(pady=(4, 14))

        self.btn_iniciar = tb.Button(
            acciones,
            text="⚙️ Iniciar configuración",
            bootstyle="primary",
            command=self.on_iniciar_callback
        )
        self.btn_iniciar.grid(row=0, column=0, padx=10, ipadx=10, ipady=6)

        self.btn_salir = tb.Button(
            acciones,
            text="✖ Salir",
            bootstyle="danger-outline",
            command=self.on_salir_callback
        )
        self.btn_salir.grid(row=0, column=1, padx=10, ipadx=10, ipady=6)

        # Progreso checador
        self.progress_frame = tb.Frame(card)
        self.progress_frame.pack(fill="x", pady=(6, 8))

        self.progress_checador = tb.Progressbar(
            self.progress_frame,
            bootstyle="success-striped",
            mode="determinate"
        )
        self.progress_checador.pack(fill="x")

        self.btn_cancelar = tb.Button(
            self.progress_frame,
            text="⛔ Cancelar búsqueda",
            bootstyle="warning",
            command=self.on_cancelar_callback
        )
        self.btn_cancelar.pack(pady=(10, 0))

        # Ocultar al inicio
        self.progress_checador.pack_forget()
        self.btn_cancelar.pack_forget()

        # Estados
        estados = tb.Frame(card)
        estados.pack(pady=(6, 2))

        self.estado_checador = tb.Label(
            estados,
            text="Estado Checador: ⏳ Esperando conexión…",
            style="Muted.TLabel"
        )
        self.estado_checador.pack(pady=(0, 4))

        self.estado_mongo = tb.Label(
            estados,
            text="Estado MongoDB: ❌ Sin conexión",
            style="Danger.TLabel"
        )
        self.estado_mongo.pack()

        # Barra Mongo (indeterminada)
        self.progress_mongo = tb.Progressbar(
            self.window,
            mode="indeterminate",
            bootstyle="info-striped"
        )
        self.progress_mongo.pack_forget()

    # =============================
    # Métodos públicos (para controller)
    # =============================

    def mostrar_progreso_mongo(self):
        self.progress_mongo.pack()
        self.progress_mongo.start()

    def ocultar_progreso_mongo(self):
        self.progress_mongo.stop()
        self.progress_mongo.pack_forget()

    def set_estado_mongo(self, texto, tipo="muted"):
        estilos = {
            "success": "Success.TLabel",
            "danger": "Danger.TLabel",
            "muted": "Muted.TLabel"
        }
        self.estado_mongo.config(text=texto, style=estilos.get(tipo, "Muted.TLabel"))

    def set_estado_checador(self, texto, tipo="muted"):
        estilos = {
            "success": "Success.TLabel",
            "danger": "Danger.TLabel",
            "muted": "Muted.TLabel"
        }
        self.estado_checador.config(text=texto, style=estilos.get(tipo, "Muted.TLabel"))

    def set_busqueda_en_progreso(self, en_progreso: bool):
        if en_progreso:
            self.btn_iniciar.config(state="disabled")
            self.btn_salir.config(state="disabled")
            self.progress_checador.pack(fill="x")
            self.btn_cancelar.pack(pady=(10, 0))
        else:
            self.btn_iniciar.config(state="normal")
            self.btn_salir.config(state="normal")
            self.progress_checador.pack_forget()
            self.btn_cancelar.pack_forget()

    def actualizar_progreso_checador(self, done, total, mensaje):
        if total > 0:
            self.progress_checador["maximum"] = total
            self.progress_checador["value"] = done

        self.set_estado_checador(mensaje)

    def iniciar(self):
        self.window.mainloop()