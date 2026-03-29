from threading import Thread, Event
import time

from ui.screens.inicio_screen import InicioScreen
from ui.dialogs.confirmar_sede_dialog import ConfirmarSedeDialog
from ui.dialogs.seleccion_sede_dialog import SeleccionSedeDialog
from ui.dialogs.password_dialog import PasswordDialog

from services.mongo_service import conectar_mongo, obtener_trabajadores, obtener_sede_por_id, obtener_sedes
from services.checador_service import buscar_checador
from services.sede_service import detectar_sede_por_checador
from services.config_service import guardar_configuracion
from services.navigation_service import ir_a_menu


class InicioController:
    def __init__(self):
        self.stop_event = Event()
        self.cliente_mongo = None

        self.screen = InicioScreen(
            on_iniciar_callback=self.iniciar_configuracion,
            on_salir_callback=self.salir,
            on_cancelar_callback=self.cancelar_busqueda
        )

        self.screen.window.protocol("WM_DELETE_WINDOW", self.salir)

    # =============================
    # Flujo principal
    # =============================
    def iniciar(self):
        self.screen.iniciar()

    def iniciar_configuracion(self):
        self.screen.set_estado_mongo("⏳ Intentando conectar a MongoDB...", "muted")
        self.screen.set_estado_checador("Estado Checador: ⏳ Esperando conexión...", "muted")
        self.screen.mostrar_progreso_mongo()

        Thread(target=self._proceso_configuracion, daemon=True).start()

    def _proceso_configuracion(self):
        try:
            # =============================
            # 1. Conexión a Mongo
            # =============================
            time.sleep(1.5)

            cliente, mensaje_mongo = conectar_mongo()

            self.screen.window.after(0, self.screen.ocultar_progreso_mongo)

            if cliente:
                self.cliente_mongo = cliente
                self.screen.window.after(
                    0,
                    lambda: self.screen.set_estado_mongo(mensaje_mongo, "success")
                )
            else:
                self.screen.window.after(
                    0,
                    lambda: self.screen.set_estado_mongo(mensaje_mongo, "danger")
                )
                return

            time.sleep(1)

            # =============================
            # 2. Buscar checador
            # =============================
            self.stop_event.clear()
            self.screen.window.after(0, lambda: self.screen.set_busqueda_en_progreso(True))
            self.screen.window.after(
                0,
                lambda: self.screen.set_estado_checador("🔎 Buscando checador en red local...", "muted")
            )

            def progress(done, total, mensaje):
                self.screen.window.after(
                    0,
                    lambda: self.screen.actualizar_progreso_checador(done, total, mensaje)
                )

            ip_detectada, usuarios = buscar_checador(
                progress_callback=progress,
                stop_event=self.stop_event
            )

            if not ip_detectada:
                self.screen.window.after(0, lambda: self.screen.set_busqueda_en_progreso(False))

                if self.stop_event.is_set():
                    self.screen.window.after(
                        0,
                        lambda: self.screen.set_estado_checador("⛔ Búsqueda cancelada.", "danger")
                    )
                else:
                    self.screen.window.after(
                        0,
                        lambda: self.screen.set_estado_checador(
                            "❌ No se encontró ningún checador disponible",
                            "danger"
                        )
                    )
                return
            
            self.ip_checador = ip_detectada

            self.screen.window.after(0, lambda: self.screen.set_busqueda_en_progreso(False))
            self.screen.window.after(
                0,
                lambda: self.screen.set_estado_checador(
                    f"✅ Checador detectado en {ip_detectada} ({len(usuarios)} usuarios)",
                    "success"
                )
            )

            # =============================
            # 3. Detección de sede
            # =============================
            trabajadores = obtener_trabajadores(self.cliente_mongo)

            resultado_sede = detectar_sede_por_checador(
                usuarios_checador=usuarios,
                trabajadores_mongo=trabajadores
            )

            if resultado_sede.get("decision") == "auto":
                sede_id = resultado_sede["sede"]
                porcentaje = resultado_sede["porcentaje"]

                sede_doc = obtener_sede_por_id(self.cliente_mongo, sede_id)
                sede_nombre = sede_doc["nombre"] if sede_doc else f"Sede {sede_id}"

                def abrir_dialogo():
                    dialogo = ConfirmarSedeDialog(
                        parent=self.screen.window,
                        sede_id=sede_id,
                        sede_nombre=sede_nombre,
                        porcentaje=porcentaje
                    )

                    print("Resultado diálogo auto:", dialogo.resultado)

                    if dialogo.resultado == "manual":
                        self._manejar_seleccion_manual_sede()
                    elif dialogo.resultado == "confirmar":
                        print(f"✅ Sede confirmada automáticamente: {sede_id} - {sede_nombre}")

                        guardar_configuracion(
                            sede_id=sede_id,
                            nombre_sede=sede_nombre,
                            checador_ip=self.ip_checador
                        )

                        self.screen.window.destroy()
                        ir_a_menu()
                self.screen.window.after(0, abrir_dialogo)

            elif resultado_sede.get("decision") == "manual":
                self.screen.window.after(0, self._manejar_seleccion_manual_sede)

        except Exception as e:
            self.screen.window.after(0, self.screen.ocultar_progreso_mongo)
            self.screen.window.after(0, lambda: self.screen.set_busqueda_en_progreso(False))
            self.screen.window.after(
                0,
                lambda: self.screen.set_estado_checador(f"❌ Error en configuración: {e}", "danger")
            )

    def _manejar_seleccion_manual_sede(self):
        sedes = obtener_sedes(self.cliente_mongo)

        dialogo_sede = SeleccionSedeDialog(
            parent=self.screen.window,
            sedes=sedes
        )

        if dialogo_sede.resultado is None:
            print("Selección manual cancelada")
            return

        sede_id = dialogo_sede.resultado
        sede_doc = obtener_sede_por_id(self.cliente_mongo, sede_id)

        if not sede_doc:
            print("No se encontró la sede seleccionada")
            return

        dialogo_password = PasswordDialog(
            parent=self.screen.window,
            titulo="Contraseña requerida",
            mensaje=f"Ingrese la contraseña para la sede '{sede_doc.get('nombre', 'Sin nombre')}':"
        )

        if dialogo_password.resultado is None:
            print("Validación de contraseña cancelada")
            return

        password_ingresada = dialogo_password.resultado
        password_real = str(sede_doc.get("password", "")).strip()

        if password_ingresada == password_real:
            nombre = sede_doc.get("nombre")

            print(f"✅ Sede seleccionada manualmente: {sede_id} - {nombre}")

            guardar_configuracion(
                sede_id=sede_id,
                nombre_sede=nombre,
                checador_ip=self.ip_checador
            )
            self.screen.window.destroy()
            ir_a_menu()
        else:
            print("❌ Contraseña incorrecta")

    # =============================
    # Eventos UI
    # =============================
    def cancelar_busqueda(self):
        self.stop_event.set()
        self.screen.set_estado_checador("⛔ Cancelando búsqueda...", "danger")

    def salir(self):
        self.stop_event.set()
        self.screen.window.destroy()