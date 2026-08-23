import tkinter as tk
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
        on_obtener_asistencias_callback,
        on_agregar_trabajadores_callback,
        on_eliminar_trabajadores_callback,
        on_sincronizacion_completa_callback,
        on_iniciar_auto_sync_callback,
        on_detener_auto_sync_callback,
        on_limpiar_callback,
        on_reconfigurar_callback,
        on_salir_callback,
        config_data=None
    ):

        # ==========================================================
        # VENTANA PRINCIPAL
        # ==========================================================

        self.window = tb.Window(
            themename="cosmo"
        )

        self.window.title(
            "Menú principal - Alu Asistencias"
        )

        self.window.geometry(
            "860x620"
        )

        self.window.resizable(
            False,
            False
        )

        # ==========================================================
        # ICONO
        # ==========================================================

        icon_path = obtener_ruta_recurso(
            "icono.ico"
        )

        if icon_path.exists():
            try:
                self.window.iconbitmap(
                    str(icon_path)
                )
            except Exception:
                pass

        # ==========================================================
        # ESTILOS
        # ==========================================================

        configure_app_style(
            self.window
        )

        # ==========================================================
        # CALLBACKS MANUALES
        # ==========================================================

        self.on_obtener_asistencias_callback = (
            on_obtener_asistencias_callback
        )

        self.on_agregar_trabajadores_callback = (
            on_agregar_trabajadores_callback
        )

        self.on_eliminar_trabajadores_callback = (
            on_eliminar_trabajadores_callback
        )

        self.on_sincronizacion_completa_callback = (
            on_sincronizacion_completa_callback
        )

        # ==========================================================
        # CALLBACKS GENERALES
        # ==========================================================

        self.on_iniciar_auto_sync_callback = (
            on_iniciar_auto_sync_callback
        )

        self.on_detener_auto_sync_callback = (
            on_detener_auto_sync_callback
        )

        self.on_limpiar_callback = (
            on_limpiar_callback
        )

        self.on_reconfigurar_callback = (
            on_reconfigurar_callback
        )

        self.on_salir_callback = (
            on_salir_callback
        )

        # ==========================================================
        # CONFIGURACION
        # ==========================================================

        self.config_data = (
            config_data or {}
        )

        # ==========================================================
        # REFERENCIA A VENTANA MANUAL
        # ==========================================================

        self.ventana_manual = None

        # ==========================================================
        # CONSTRUIR INTERFAZ
        # ==========================================================

        self._build_ui()

    # ==============================================================
    # INTERFAZ PRINCIPAL
    # ==============================================================

    def _build_ui(self):

        # ==========================================================
        # TARJETA PRINCIPAL
        # ==========================================================

        card = tb.Frame(
            self.window,
            padding=(28, 24),
            style="Card.TFrame"
        )

        card.pack(
            expand=True,
            padx=28,
            pady=28,
            fill="both"
        )

        # ==========================================================
        # TITULO
        # ==========================================================

        titulo = tb.Label(
            card,
            text="Menú principal · Alu Asistencias",
            style="Title.TLabel"
        )

        titulo.pack(
            pady=(6, 4)
        )
        # ==========================================================
        # INFORMACION DE LA SEDE
        # ==========================================================

        info_frame = tb.Frame(
            card,
            style="Card.TFrame"
        )

        info_frame.pack(
            pady=(0, 18),
            fill="x"
        )

        sede = self.config_data.get(
            "nombre_sede",
            "No disponible"
        )

        sede_id = self.config_data.get(
            "sede",
            "N/D"
        )

        ip = self.config_data.get(
            "checador_ip",
            "N/D"
        )

        tb.Label(
            info_frame,
            text=f"📍 Sede: {sede}",
            style="Muted.TLabel"
        ).pack(
            anchor="w",
            pady=2
        )

        tb.Label(
            info_frame,
            text=f"🆔 ID sede: {sede_id}",
            style="Muted.TLabel"
        ).pack(
            anchor="w",
            pady=2
        )

        tb.Label(
            info_frame,
            text=f"📡 Checador: {ip}",
            style="Muted.TLabel"
        ).pack(
            anchor="w",
            pady=2
        )

        # ==========================================================
        # BOTONES PRINCIPALES
        # ==========================================================

        acciones = tb.Frame(
            card,
            style="Card.TFrame"
        )

        acciones.pack(
            pady=(10, 0)
        )

        # ----------------------------------------------------------
        # SINCRONIZACION MANUAL
        # ----------------------------------------------------------

        self.btn_sync_manual = tb.Button(
            acciones,
            text="🔄 Sincronización manual",
            bootstyle="primary",
            command=self.abrir_menu_sincronizacion_manual
        )

        self.btn_sync_manual.grid(
            row=0,
            column=0,
            padx=10,
            pady=10,
            ipadx=10,
            ipady=6
        )

        # ----------------------------------------------------------
        # INICIAR AUTO SYNC
        # ----------------------------------------------------------

        self.btn_auto_on = tb.Button(
            acciones,
            text="▶ Iniciar auto sync",
            bootstyle="success",
            command=self.on_iniciar_auto_sync_callback
        )

        self.btn_auto_on.grid(
            row=0,
            column=1,
            padx=10,
            pady=10,
            ipadx=10,
            ipady=6
        )

        # ----------------------------------------------------------
        # DETENER AUTO SYNC
        # ----------------------------------------------------------

        self.btn_auto_off = tb.Button(
            acciones,
            text="⏹ Detener auto sync",
            bootstyle="info",
            command=self.on_detener_auto_sync_callback
        )

        self.btn_auto_off.grid(
            row=0,
            column=2,
            padx=10,
            pady=10,
            ipadx=10,
            ipady=6
        )

        # ----------------------------------------------------------
        # RECONFIGURAR
        # ----------------------------------------------------------

        self.btn_reconfigurar = tb.Button(
            acciones,
            text="⚙️ Reconfigurar",
            bootstyle="warning",
            command=self.on_reconfigurar_callback
        )

        self.btn_reconfigurar.grid(
            row=1,
            column=0,
            padx=10,
            pady=10,
            ipadx=10,
            ipady=6
        )

        # ----------------------------------------------------------
        # SALIR
        # ----------------------------------------------------------

        self.btn_salir = tb.Button(
            acciones,
            text="✖ Salir",
            bootstyle="danger-outline",
            command=self.on_salir_callback
        )

        self.btn_salir.grid(
            row=1,
            column=1,
            padx=10,
            pady=10,
            ipadx=10,
            ipady=6
        )

        # ----------------------------------------------------------
        # LIMPIAR CHECADOR
        # ----------------------------------------------------------

        self.btn_limpiar = tb.Button(
            acciones,
            text="🧹 Limpiar checador",
            bootstyle="secondary",
            command=self.on_limpiar_callback
        )

        self.btn_limpiar.grid(
            row=1,
            column=2,
            padx=10,
            pady=10,
            ipadx=10,
            ipady=6
        )

        # ==========================================================
        # ESTADO AUTO SYNC
        # ==========================================================

        estado_auto_frame = tb.Frame(
            card,
            style="Card.TFrame"
        )

        estado_auto_frame.pack(
            pady=(18, 6),
            fill="x"
        )

        self.auto_sync_label = tb.Label(
            estado_auto_frame,
            text="Auto sync: desactivada",
            style="Muted.TLabel"
        )

        self.auto_sync_label.pack(
            anchor="w",
            pady=2
        )

        self.proxima_sync_label = tb.Label(
            estado_auto_frame,
            text="Próxima ejecución: no programada",
            style="Muted.TLabel"
        )

        self.proxima_sync_label.pack(
            anchor="w",
            pady=2
        )

        # ==========================================================
        # BARRA DE PROGRESO
        # ==========================================================

        self.progress = ttk.Progressbar(
            card,
            mode="indeterminate",
            length=100
        )

        self.progress.pack(
            fill="x",
            pady=(12, 8)
        )

        self.progress.pack_forget()

        # ==========================================================
        # ESTADO GENERAL
        # ==========================================================

        self.estado_label = tb.Label(
            card,
            text="Estado: Sistema listo",
            style="Success.TLabel"
        )

        self.estado_label.pack(
            pady=(12, 0)
        )

    # ==============================================================
    # MENU DE SINCRONIZACION MANUAL
    # ==============================================================

    def abrir_menu_sincronizacion_manual(self):

        # ==========================================================
        # EVITAR ABRIR DOS VENTANAS
        # ==========================================================

        if (
            self.ventana_manual is not None
            and self.ventana_manual.winfo_exists()
        ):
            self.ventana_manual.lift()
            self.ventana_manual.focus_force()
            return

        # ==========================================================
        # CREAR VENTANA
        # ==========================================================

        self.ventana_manual = tb.Toplevel(
            self.window
        )

        self.ventana_manual.title(
            "Sincronización manual"
        )

        ancho = 540
        alto = 560

        self.ventana_manual.geometry(
            f"{ancho}x{alto}"
        )

        # No permitimos modificar ancho,
        # pero sí aumentar/disminuir altura.
        self.ventana_manual.resizable(
            False,
            True
        )

        # Asociar la ventana al menú principal
        self.ventana_manual.transient(
            self.window
        )

        # Bloquear temporalmente interacción con ventana principal
        self.ventana_manual.grab_set()

        # ==========================================================
        # ICONO
        # ==========================================================

        icon_path = obtener_ruta_recurso(
            "icono.ico"
        )

        if icon_path.exists():
            try:
                self.ventana_manual.iconbitmap(
                    str(icon_path)
                )
            except Exception:
                pass

        # ==========================================================
        # CENTRAR VENTANA
        # ==========================================================

        self.ventana_manual.update_idletasks()

        x = (
            self.window.winfo_x()
            + (self.window.winfo_width() // 2)
            - (ancho // 2)
        )

        y = (
            self.window.winfo_y()
            + (self.window.winfo_height() // 2)
            - (alto // 2)
        )

        self.ventana_manual.geometry(
            f"{ancho}x{alto}+{x}+{y}"
        )

        # ==========================================================
        # CONTENEDOR DEL SCROLL
        # ==========================================================

        contenedor_scroll = tb.Frame(
            self.ventana_manual
        )

        contenedor_scroll.pack(
            fill="both",
            expand=True
        )

        # ==========================================================
        # CANVAS
        # ==========================================================

        canvas = tk.Canvas(
            contenedor_scroll,
            highlightthickness=0,
            borderwidth=0
        )

        canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        # ==========================================================
        # SCROLLBAR VERTICAL
        # ==========================================================

        scrollbar = ttk.Scrollbar(
            contenedor_scroll,
            orient="vertical",
            command=canvas.yview
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        canvas.configure(
            yscrollcommand=scrollbar.set
        )

        # ==========================================================
        # CONTENIDO INTERNO DEL CANVAS
        # ==========================================================

        card = tb.Frame(
            canvas,
            padding=(24, 20)
        )

        ventana_canvas = canvas.create_window(
            (0, 0),
            window=card,
            anchor="nw"
        )

        # ==========================================================
        # ACTUALIZAR REGION DEL SCROLL
        # ==========================================================

        def actualizar_scroll(event=None):
            canvas.configure(
                scrollregion=canvas.bbox("all")
            )

        # Hace que el frame interno ocupe todo el ancho disponible
        def ajustar_ancho(event):
            canvas.itemconfigure(
                ventana_canvas,
                width=event.width
            )

        card.bind(
            "<Configure>",
            actualizar_scroll
        )

        canvas.bind(
            "<Configure>",
            ajustar_ancho
        )

        # ==========================================================
        # SCROLL CON RUEDA DEL MOUSE
        # ==========================================================

        def scroll_mouse(event):

            canvas.yview_scroll(
                int(-1 * (event.delta / 120)),
                "units"
            )

        self.ventana_manual.bind(
            "<MouseWheel>",
            scroll_mouse
        )

        # ==========================================================
        # TITULO
        # ==========================================================

        tb.Label(
            card,
            text="Sincronización manual",
            font=("Segoe UI", 17, "bold")
        ).pack(
            pady=(5, 5)
        )

        tb.Label(
            card,
            text=(
                "Selecciona únicamente la acción "
                "que deseas ejecutar."
            ),
            bootstyle="secondary",
            wraplength=450,
            justify="center"
        ).pack(
            pady=(0, 22)
        )

        # ==========================================================
        # OBTENER ASISTENCIAS
        # ==========================================================

        self._crear_boton_manual(
            parent=card,
            texto="📥 Obtener asistencias",
            descripcion=(
                "Lee las marcas del checador, "
                "las consolida y las guarda en MongoDB."
            ),
            estilo="primary",
            callback=self.on_obtener_asistencias_callback
        )

        # ==========================================================
        # AGREGAR TRABAJADORES
        # ==========================================================

        self._crear_boton_manual(
            parent=card,
            texto="👤 Agregar trabajadores faltantes",
            descripcion=(
                "Agrega al checador los trabajadores "
                "activos de esta sede que todavía no existen."
            ),
            estilo="success",
            callback=self.on_agregar_trabajadores_callback
        )

        # ==========================================================
        # ELIMINAR TRABAJADORES
        # ==========================================================

        self._crear_boton_manual(
            parent=card,
            texto="🗑 Eliminar trabajadores fuera de sede",
            descripcion=(
                "Elimina del checador únicamente usuarios "
                "que ya no pertenecen a esta sede, "
                "respetando las protecciones."
            ),
            estilo="danger",
            callback=self.on_eliminar_trabajadores_callback
        )

        # ==========================================================
        # CERRAR
        # ==========================================================

        tb.Button(
            card,
            text="Cerrar",
            bootstyle="secondary-outline",
            command=self._cerrar_menu_manual
        ).pack(
            pady=(20, 15),
            ipadx=20,
            ipady=4
        )

        # ==========================================================
        # CERRAR CON X
        # ==========================================================

        self.ventana_manual.protocol(
            "WM_DELETE_WINDOW",
            self._cerrar_menu_manual
        )

    # ==============================================================
    # CREAR BOTON DEL MENU MANUAL
    # ==============================================================

    def _crear_boton_manual(
        self,
        parent,
        texto,
        descripcion,
        estilo,
        callback
    ):

        frame = tb.Frame(
            parent
        )

        frame.pack(
            fill="x",
            pady=6
        )

        boton = tb.Button(
            frame,
            text=texto,
            bootstyle=estilo,
            command=lambda: self._ejecutar_accion_manual(
                callback
            )
        )

        boton.pack(
            fill="x",
            ipady=5
        )

        tb.Label(
            frame,
            text=descripcion,
            bootstyle="secondary",
            wraplength=430,
            justify="left"
        ).pack(
            anchor="w",
            pady=(3, 0)
        )

    # ==============================================================
    # EJECUTAR ACCION MANUAL
    # ==============================================================

    def _ejecutar_accion_manual(
        self,
        callback
    ):

        # Primero cerrar el menu manual
        self._cerrar_menu_manual()

        # Después ejecutar la accion seleccionada
        callback()

    # ==============================================================
    # CERRAR MENU MANUAL
    # ==============================================================

    def _cerrar_menu_manual(self):

        if (
            self.ventana_manual is not None
            and self.ventana_manual.winfo_exists()
        ):

            try:
                self.ventana_manual.grab_release()
            except Exception:
                pass

            self.ventana_manual.destroy()

        self.ventana_manual = None

    # ==============================================================
    # ESTADO GENERAL
    # ==============================================================

    def set_estado(
        self,
        texto,
        tipo="muted"
    ):

        estilos = {
            "success": "Success.TLabel",
            "danger": "Danger.TLabel",
            "muted": "Muted.TLabel"
        }

        self.estado_label.config(
            text=texto,
            style=estilos.get(
                tipo,
                "Muted.TLabel"
            )
        )

    # ==============================================================
    # ESTADO AUTO SYNC
    # ==============================================================

    def set_estado_auto_sync(
        self,
        texto,
        tipo="muted"
    ):

        estilos = {
            "success": "Success.TLabel",
            "danger": "Danger.TLabel",
            "muted": "Muted.TLabel"
        }

        self.auto_sync_label.config(
            text=texto,
            style=estilos.get(
                tipo,
                "Muted.TLabel"
            )
        )

    # ==============================================================
    # PROXIMA SINCRONIZACION
    # ==============================================================

    def set_proxima_sync(
        self,
        texto,
        tipo="muted"
    ):

        estilos = {
            "success": "Success.TLabel",
            "danger": "Danger.TLabel",
            "muted": "Muted.TLabel"
        }

        self.proxima_sync_label.config(
            text=texto,
            style=estilos.get(
                tipo,
                "Muted.TLabel"
            )
        )

    # ==============================================================
    # PROGRESO
    # ==============================================================

    def mostrar_progreso(self):

        self.progress.pack(
            fill="x",
            pady=(12, 8)
        )

        self.progress.start(
            10
        )

    def ocultar_progreso(self):

        self.progress.stop()

        self.progress.pack_forget()

    # ==============================================================
    # INICIAR INTERFAZ
    # ==============================================================

    def iniciar(self):

        self.window.mainloop()