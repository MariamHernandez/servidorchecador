from controllers.inicio_controller import InicioController
from controllers.menu_controller import MenuController
from services.config_service import cargar_configuracion


def main():
    config = cargar_configuracion()

    if config and config.get("setup_done"):
        print("Configuracion existente detectada. Abriendo menu...")
        controller = MenuController()
        controller.iniciar()
        return

    controller = InicioController()
    controller.iniciar()


if __name__ == "__main__":
    main()