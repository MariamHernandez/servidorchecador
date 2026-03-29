import ttkbootstrap as tb

from ui.styles.theme import configure_app_style


class MenuScreen:
    def __init__(
        self,
        on_sincronizacion_manual_callback,
        on_reconfigurar_callback,
        on_salir_callback,
        config_data=None
    ):
        self.window = tb.Window(themename="cosmo")
        self.window.title("Menú principal - Alu Asistencias")
        self.window.geometry("860x520")
        self.window.resizable(False, False)

        configure_app_style(self.window)

        self.on_sincronizacion_manual_callback = on_sincronizacion_manual_callback
        self.on_reconfigurar_callback = on_reconfigurar_callback
        self.on_salir_callback = on_salir_callback
        self.config_data = config_data or {}

        self._build_ui()

    def _build_ui(self):
        card = tb.Frame(self.window, padding=(28, 24), style="Card.TFrame")
        card.pack(expand=True, padx=28, pady=28, fill="both")

        titulo = tb.Label(
            card,
            text="🏠 Menú principal · Alu Asistencias",
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

        self.btn_reconfigurar = tb.Button(
            acciones,
            text="⚙️ Reconfigurar",
            bootstyle="warning",
            command=self.on_reconfigurar_callback
        )
        self.btn_reconfigurar.grid(row=0, column=1, padx=10, pady=10, ipadx=10, ipady=6)

        self.btn_salir = tb.Button(
            acciones,
            text="✖ Salir",
            bootstyle="danger-outline",
            command=self.on_salir_callback
        )
        self.btn_salir.grid(row=0, column=2, padx=10, pady=10, ipadx=10, ipady=6)

        self.estado_label = tb.Label(
            card,
            text="Estado: ✅ Sistema listo",
            style="Success.TLabel"
        )
        self.estado_label.pack(pady=(20, 0))

    def set_estado(self, texto, tipo="muted"):
        estilos = {
            "success": "Success.TLabel",
            "danger": "Danger.TLabel",
            "muted": "Muted.TLabel"
        }
        self.estado_label.config(text=texto, style=estilos.get(tipo, "Muted.TLabel"))

    def iniciar(self):
        self.window.mainloop()