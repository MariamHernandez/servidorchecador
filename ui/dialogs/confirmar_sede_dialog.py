import ttkbootstrap as tb
from ui.styles.theme import LIGHT_BG


class ConfirmarSedeDialog:
    def __init__(self, parent, sede_id, sede_nombre, porcentaje):
        self.resultado = None

        self.window = tb.Toplevel(parent)
        self.window.title("Sede detectada automáticamente")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()
        self.window.focus_force()
        self.window.configure(background=LIGHT_BG)

        self._build_ui(sede_id, sede_nombre, porcentaje)
        self._centrar(parent)

        self.window.wait_window()

    def _build_ui(self, sede_id, sede_nombre, porcentaje):
        card = tb.Frame(self.window, padding=(32, 28), style="Card.TFrame")
        card.grid(row=0, column=0, sticky="nsew")

        titulo = tb.Label(
            card,
            text="Sede detectada automáticamente ✅",
            font=("Segoe UI Semibold", 14, "bold"),
            background=LIGHT_BG,
            foreground="#212529",
            anchor="w"
        )
        titulo.grid(row=0, column=0, sticky="w", pady=(6, 12))

        mensaje = (
            f"Se detectó automáticamente la sede:\n\n"
            f"ID: {sede_id}\n"
            f"Nombre: {sede_nombre}\n"
            f"Coincidencia: {porcentaje:.1f}%\n\n"
            f"¿Deseas continuar con esta configuración?"
        )

        cuerpo = tb.Label(
            card,
            text=mensaje,
            font=("Segoe UI", 11),
            justify="left",
            anchor="w",
            wraplength=420,
            background=LIGHT_BG,
            foreground="#333333"
        )
        cuerpo.grid(row=1, column=0, sticky="ew", pady=(0, 18))

        tb.Separator(card).grid(row=2, column=0, sticky="ew", pady=(0, 16))

        botones = tb.Frame(card, style="Card.TFrame")
        botones.grid(row=3, column=0, sticky="e")

        tb.Button(
            botones,
            text="Elegir manualmente",
            bootstyle="danger-outline",
            command=self._elegir_manual
        ).grid(row=0, column=0, padx=(0, 10))

        tb.Button(
            botones,
            text="Confirmar",
            bootstyle="success",
            command=self._confirmar
        ).grid(row=0, column=1)

    def _confirmar(self):
        self.resultado = "confirmar"
        self.window.destroy()

    def _elegir_manual(self):
        self.resultado = "manual"
        self.window.destroy()

    def _centrar(self, parent):
        self.window.update_idletasks()
        try:
            x = parent.winfo_rootx() + (parent.winfo_width() - self.window.winfo_width()) // 2
            y = parent.winfo_rooty() + (parent.winfo_height() - self.window.winfo_height()) // 2
            self.window.geometry(f"+{max(0, x)}+{max(0, y)}")
        except Exception:
            pass