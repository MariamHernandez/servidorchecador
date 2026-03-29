import ttkbootstrap as tb
from tkinter import ttk
from ui.styles.theme import LIGHT_BG


class SeleccionSedeDialog:
    def __init__(self, parent, sedes):
        self.resultado = None
        self.sedes = sedes or []

        self.window = tb.Toplevel(parent)
        self.window.title("Selección manual de sede")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()
        self.window.focus_force()
        self.window.configure(background=LIGHT_BG)

        self._build_ui()
        self._centrar(parent)

        self.window.wait_window()

    def _build_ui(self):
        card = tb.Frame(self.window, padding=(30, 26), style="Card.TFrame")
        card.grid(row=0, column=0, sticky="nsew")

        titulo = tb.Label(
            card,
            text="Selecciona la sede manualmente",
            font=("Segoe UI Semibold", 14, "bold"),
            background=LIGHT_BG,
            foreground="#212529"
        )
        titulo.grid(row=0, column=0, sticky="w", pady=(0, 12))

        descripcion = tb.Label(
            card,
            text="No se usará la sede detectada automáticamente. Elige la sede correcta para este checador.",
            font=("Segoe UI", 11),
            justify="left",
            wraplength=420,
            background=LIGHT_BG
        )
        descripcion.grid(row=1, column=0, sticky="w", pady=(0, 14))

        opciones = [f"{s['id']} - {s['nombre']}" for s in self.sedes]

        self.combo_sedes = ttk.Combobox(
            card,
            values=opciones,
            state="readonly",
            font=("Segoe UI", 11),
            width=38
        )
        self.combo_sedes.grid(row=2, column=0, sticky="ew", pady=(0, 16))

        if opciones:
            self.combo_sedes.current(0)

        botones = tb.Frame(card, style="Card.TFrame")
        botones.grid(row=3, column=0, sticky="e")

        tb.Button(
            botones,
            text="Cancelar",
            bootstyle="danger-outline",
            command=self._cancelar
        ).grid(row=0, column=0, padx=(0, 10))

        tb.Button(
            botones,
            text="Continuar",
            bootstyle="primary",
            command=self._confirmar
        ).grid(row=0, column=1)

        self.window.bind("<Return>", lambda event: self._confirmar())
        self.window.bind("<Escape>", lambda event: self._cancelar())

    def _confirmar(self):
        seleccion = self.combo_sedes.get().strip()

        if not seleccion:
            self.resultado = None
            self.window.destroy()
            return

        sede_id = int(seleccion.split(" - ")[0])
        self.resultado = sede_id
        self.window.destroy()

    def _cancelar(self):
        self.resultado = None
        self.window.destroy()

    def _centrar(self, parent):
        self.window.update_idletasks()
        try:
            x = parent.winfo_rootx() + (parent.winfo_width() - self.window.winfo_width()) // 2
            y = parent.winfo_rooty() + (parent.winfo_height() - self.window.winfo_height()) // 2
            self.window.geometry(f"+{max(0, x)}+{max(0, y)}")
        except Exception:
            pass