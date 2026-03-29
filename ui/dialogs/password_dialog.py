import ttkbootstrap as tb
from tkinter import ttk
from ui.styles.theme import LIGHT_BG


class PasswordDialog:
    def __init__(self, parent, titulo="Contraseña requerida", mensaje="Ingrese la contraseña:"):
        self.resultado = None

        self.window = tb.Toplevel(parent)
        self.window.title(titulo)
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()
        self.window.focus_force()
        self.window.configure(background=LIGHT_BG)

        self._build_ui(mensaje)
        self._centrar(parent)

        self.window.wait_window()

    def _build_ui(self, mensaje):
        card = tb.Frame(self.window, padding=(28, 24), style="Card.TFrame")
        card.grid(row=0, column=0, sticky="nsew")

        label = tb.Label(
            card,
            text=mensaje,
            font=("Segoe UI", 11),
            justify="left",
            wraplength=340,
            background=LIGHT_BG
        )
        label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        self.entry_password = ttk.Entry(card, show="*", font=("Segoe UI", 11), width=30)
        self.entry_password.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 16))
        self.entry_password.focus_set()

        btn_cancelar = tb.Button(
            card,
            text="Cancelar",
            bootstyle="danger-outline",
            command=self._cancelar
        )
        btn_cancelar.grid(row=2, column=0, padx=(0, 8), sticky="e")

        btn_confirmar = tb.Button(
            card,
            text="Confirmar",
            bootstyle="success",
            command=self._confirmar
        )
        btn_confirmar.grid(row=2, column=1, sticky="w")

        self.window.bind("<Return>", lambda event: self._confirmar())
        self.window.bind("<Escape>", lambda event: self._cancelar())

    def _confirmar(self):
        self.resultado = self.entry_password.get().strip()
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