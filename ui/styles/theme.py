import ttkbootstrap as tb

LIGHT_BG = "#f5f6f7"
MUTED = "#6c757d"
SUCCESS = "#198754"
DANGER = "#dc3545"
TEXT_DARK = "#212529"


def configure_app_style(window):
    window.configure(background=LIGHT_BG)

    style = tb.Style()

    style.configure("TFrame", background=LIGHT_BG)
    style.configure("TLabel", background=LIGHT_BG)

    style.configure("Card.TFrame", background=LIGHT_BG)
    style.configure("Title.TLabel", background=LIGHT_BG, font=("Segoe UI", 20, "bold"))
    style.configure("Subtitle.TLabel", background=LIGHT_BG, foreground=MUTED, font=("Segoe UI", 11))
    style.configure("Muted.TLabel", background=LIGHT_BG, foreground=MUTED, font=("Segoe UI", 10))
    style.configure("Success.TLabel", background=LIGHT_BG, foreground=SUCCESS, font=("Segoe UI", 10, "italic"))
    style.configure("Danger.TLabel", background=LIGHT_BG, foreground=DANGER, font=("Segoe UI", 10, "italic"))

    try:
        style.configure("TButton", focuscolor=LIGHT_BG)
    except Exception:
        pass

    window.option_add("*highlightThickness", 0)

    return style