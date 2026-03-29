from controllers.inicio_controller import InicioController
from services.config_service import cargar_configuracion
from services.navigation_service import ir_a_menu


def main():
    config = cargar_configuracion()

    if config and config.get("setup_done"):
        print("✅ Configuración existente detectada. Abriendo menú...")
        ir_a_menu()
        return

    controller = InicioController()
    controller.iniciar()


if __name__ == "__main__":
    main()