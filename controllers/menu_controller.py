#menu_controller.py
import threading
from tkinter import messagebox
from datetime import datetime, timedelta

from ui.screens.menu_screen import MenuScreen
from services.config_service import cargar_configuracion, eliminar_configuracion
from services.navigation_service import reiniciar_aplicacion
from services.mongo_service import (
    conectar_mongo,
    guardar_asistencias_consolidadas,
    obtener_trabajadores_activos_por_sede
)
from services.checador_service import (
    obtener_registros,
    limpiar_registros_asistencia,
    obtener_usuarios_checador,
    agregar_usuario_checador,
    eliminar_usuario_checador,
    obtener_siguiente_uid_disponible
)
from services.asistencias_service import consolidar_registros_por_dia
from services.respaldo_service import guardar_respaldo_manual


class MenuController:

    def __init__(self):
        self.config_data = cargar_configuracion() or {}

        # ==========================================
        # AUTO SYNC
        # ==========================================
        self.auto_sync_activa = False
        self.auto_sync_intervalo = 10 * 60 * 1000  # 10 minutos
        self.auto_sync_job = None
        self.proxima_sync_dt = None

        # ==========================================
        # ESTADO DE SINCRONIZACION
        # ==========================================
        self.sync_en_proceso = False

        # ==========================================
        # ANIMACION
        # ==========================================
        self.animacion_sync_activa = False
        self.animacion_sync_job = None

        # ==========================================
        # SIMULACION DE USUARIOS
        # ==========================================
        self.modo_simulacion_usuarios = False

        # ==========================================
        # INTERFAZ
        # ==========================================
        self.screen = MenuScreen(
            on_obtener_asistencias_callback=self.obtener_asistencias_manual,
            on_agregar_trabajadores_callback=self.agregar_trabajadores_manual,
            on_eliminar_trabajadores_callback=self.eliminar_trabajadores_manual,
            on_sincronizacion_completa_callback=self.sincronizacion_completa_manual,

            on_iniciar_auto_sync_callback=self.activar_auto_sync,
            on_detener_auto_sync_callback=self.desactivar_auto_sync,
            on_limpiar_callback=self.limpiar_checador,
            on_reconfigurar_callback=self.reconfigurar,
            on_salir_callback=self.salir,

            config_data=self.config_data
        )

        self.screen.window.protocol(
            "WM_DELETE_WINDOW",
            self.salir
        )

    # ==========================================================
    # INICIAR
    # ==========================================================

    def iniciar(self):
        self.screen.iniciar()

    # ==========================================================
    # MONGO
    # ==========================================================

    def _get_cliente_mongo(self):
        cliente, _ = conectar_mongo()
        return cliente

    # ==========================================================
    # EJECUTOR GENERAL DE TAREAS
    # ==========================================================

    def _iniciar_tarea_sync(self, texto, funcion, *args):

        if self.sync_en_proceso:
            self.screen.set_estado(
                "Estado: ya hay una sincronizacion en proceso...",
                "muted"
            )
            return

        self.sync_en_proceso = True

        self._iniciar_animacion_sync(texto)

        hilo = threading.Thread(
            target=funcion,
            args=args,
            daemon=True
        )

        hilo.start()

    # ==========================================================
    # SINCRONIZACION MANUAL
    # ==========================================================

    def obtener_asistencias_manual(self):

        self._iniciar_tarea_sync(
            "Estado: obteniendo asistencias",
            self._ejecutar_obtener_asistencias
        )

    def agregar_trabajadores_manual(self):

        self._iniciar_tarea_sync(
            "Estado: agregando trabajadores faltantes",
            self._ejecutar_agregar_trabajadores
        )

    def eliminar_trabajadores_manual(self):

        self._iniciar_tarea_sync(
            "Estado: eliminando trabajadores fuera de sede",
            self._ejecutar_eliminar_trabajadores
        )

    def sincronizacion_completa_manual(self):

        self._iniciar_tarea_sync(
            "Estado: ejecutando sincronizacion completa",
            self._ejecutar_sincronizacion_completa,
            "manual"
        )

    # ==========================================================
    # OBTENER ASISTENCIAS MANUAL
    # ==========================================================

    def _ejecutar_obtener_asistencias(self):

        try:

            ip = self.config_data.get("checador_ip")
            sede_id = self.config_data.get("sede")

            # ------------------------------------------
            # VALIDAR CONFIGURACION
            # ------------------------------------------

            if not ip or sede_id is None:

                self.screen.window.after(
                    0,
                    lambda: self.screen.set_estado(
                        "Estado: configuracion incompleta",
                        "danger"
                    )
                )

                return

            # ------------------------------------------
            # CONECTAR A MONGO
            # ------------------------------------------

            cliente = self._get_cliente_mongo()

            if not cliente:

                self.screen.window.after(
                    0,
                    lambda: self.screen.set_estado(
                        "Estado: no se pudo conectar a MongoDB",
                        "danger"
                    )
                )

                return

            # ------------------------------------------
            # OBTENER REGISTROS
            # ------------------------------------------

            registros = obtener_registros(ip)

            if not registros:

                self.screen.window.after(
                    0,
                    lambda: self.screen.set_estado(
                        "Estado: no se encontraron registros en el checador",
                        "muted"
                    )
                )

                return

            # ------------------------------------------
            # CONSOLIDAR
            # ------------------------------------------

            documentos = consolidar_registros_por_dia(
                registros=registros,
                sede_id=sede_id,
                origen="zkteco"
            )

            if not documentos:

                self.screen.window.after(
                    0,
                    lambda: self.screen.set_estado(
                        "Estado: no se pudieron consolidar registros validos",
                        "danger"
                    )
                )

                return

            # ------------------------------------------
            # GUARDAR EN MONGO
            # ------------------------------------------

            resumen = guardar_asistencias_consolidadas(
                cliente,
                documentos
            )

            # ------------------------------------------
            # RESPALDO LOCAL
            # ------------------------------------------

            ruta_respaldo = guardar_respaldo_manual(
                documentos=documentos,
                sede=sede_id,
                checador_ip=ip,
                resumen=resumen
            )

            # ------------------------------------------
            # RESULTADO
            # ------------------------------------------

            self.screen.window.after(
                0,
                lambda: self.screen.set_estado(
                    f"Estado: asistencias obtenidas | "
                    f"docs: {len(documentos)} | "
                    f"ins: {resumen['insertados']} | "
                    f"act: {resumen['actualizados']}",
                    "success"
                )
            )

            print("[OK] Asistencias obtenidas correctamente")
            print(
                f"[INFO] Registros leidos del checador: "
                f"{len(registros)}"
            )
            print(
                f"[INFO] Documentos consolidados: "
                f"{len(documentos)}"
            )
            print(
                f"[INFO] Respaldo guardado en: "
                f"{ruta_respaldo}"
            )
            print(
                f"[INFO] Insertados: "
                f"{resumen['insertados']}"
            )
            print(
                f"[INFO] Actualizados: "
                f"{resumen['actualizados']}"
            )

        except Exception as e:

            error_msg = str(e)

            print(
                f"[ERROR] Error obteniendo asistencias: "
                f"{error_msg}"
            )

            self.screen.window.after(
                0,
                lambda: self.screen.set_estado(
                    f"Estado: error obteniendo asistencias: "
                    f"{error_msg}",
                    "danger"
                )
            )

        finally:

            self.sync_en_proceso = False

            self.screen.window.after(
                0,
                self._detener_animacion_sync
            )

    # ==========================================================
    # AGREGAR TRABAJADORES MANUAL
    # ==========================================================

    def _ejecutar_agregar_trabajadores(self):

        try:

            ip = self.config_data.get("checador_ip")
            sede_id = self.config_data.get("sede")

            if not ip or sede_id is None:

                self.screen.window.after(
                    0,
                    lambda: self.screen.set_estado(
                        "Estado: configuracion incompleta",
                        "danger"
                    )
                )

                return

            cliente = self._get_cliente_mongo()

            if not cliente:

                self.screen.window.after(
                    0,
                    lambda: self.screen.set_estado(
                        "Estado: no se pudo conectar a MongoDB",
                        "danger"
                    )
                )

                return

            # SOLO AGREGAR
            resumen = self.sincronizar_usuarios_checador(
                cliente=cliente,
                ip=ip,
                sede_id=sede_id,
                agregar=True,
                eliminar=False
            )

            self.screen.window.after(
                0,
                lambda: self.screen.set_estado(
                    f"Estado: trabajadores agregados: "
                    f"{resumen['agregados']} | "
                    f"errores: {resumen['errores']}",
                    "success"
                )
            )

            print("[OK] Proceso de agregar trabajadores terminado")
            print(
                f"[INFO] Trabajadores agregados: "
                f"{resumen['agregados']}"
            )
            print(
                f"[INFO] Errores: "
                f"{resumen['errores']}"
            )

        except Exception as e:

            error_msg = str(e)

            print(
                f"[ERROR] Error agregando trabajadores: "
                f"{error_msg}"
            )

            self.screen.window.after(
                0,
                lambda: self.screen.set_estado(
                    f"Estado: error agregando trabajadores: "
                    f"{error_msg}",
                    "danger"
                )
            )

        finally:

            self.sync_en_proceso = False

            self.screen.window.after(
                0,
                self._detener_animacion_sync
            )

    # ==========================================================
    # ELIMINAR TRABAJADORES MANUAL
    # ==========================================================

    def _ejecutar_eliminar_trabajadores(self):

        try:

            ip = self.config_data.get("checador_ip")
            sede_id = self.config_data.get("sede")

            if not ip or sede_id is None:

                self.screen.window.after(
                    0,
                    lambda: self.screen.set_estado(
                        "Estado: configuracion incompleta",
                        "danger"
                    )
                )

                return

            cliente = self._get_cliente_mongo()

            if not cliente:

                self.screen.window.after(
                    0,
                    lambda: self.screen.set_estado(
                        "Estado: no se pudo conectar a MongoDB",
                        "danger"
                    )
                )

                return

            # SOLO ELIMINAR
            resumen = self.sincronizar_usuarios_checador(
                cliente=cliente,
                ip=ip,
                sede_id=sede_id,
                agregar=False,
                eliminar=True
            )

            self.screen.window.after(
                0,
                lambda: self.screen.set_estado(
                    f"Estado: eliminados: "
                    f"{resumen['eliminados']} | "
                    f"protegidos/ignorados: "
                    f"{resumen['ignorados']} | "
                    f"errores: {resumen['errores']}",
                    "success"
                )
            )

            print("[OK] Proceso de eliminar trabajadores terminado")
            print(
                f"[INFO] Eliminados: "
                f"{resumen['eliminados']}"
            )
            print(
                f"[INFO] Protegidos/ignorados: "
                f"{resumen['ignorados']}"
            )
            print(
                f"[INFO] Errores: "
                f"{resumen['errores']}"
            )

        except Exception as e:

            error_msg = str(e)

            print(
                f"[ERROR] Error eliminando trabajadores: "
                f"{error_msg}"
            )

            self.screen.window.after(
                0,
                lambda: self.screen.set_estado(
                    f"Estado: error eliminando trabajadores: "
                    f"{error_msg}",
                    "danger"
                )
            )

        finally:

            self.sync_en_proceso = False

            self.screen.window.after(
                0,
                self._detener_animacion_sync
            )

    # ==========================================================
    # SINCRONIZACION COMPLETA
    # MANUAL Y AUTOMATICA UTILIZAN ESTA FUNCION
    # ==========================================================

    def _ejecutar_sincronizacion_completa(
        self,
        modo="manual"
    ):

        try:

            ip = self.config_data.get("checador_ip")
            sede_id = self.config_data.get("sede")

            # ------------------------------------------
            # VALIDAR CONFIGURACION
            # ------------------------------------------

            if not ip or sede_id is None:

                self.screen.window.after(
                    0,
                    lambda: self.screen.set_estado(
                        "Estado: configuracion incompleta",
                        "danger"
                    )
                )

                return

            # ------------------------------------------
            # CONECTAR A MONGO
            # ------------------------------------------

            cliente = self._get_cliente_mongo()

            if not cliente:

                self.screen.window.after(
                    0,
                    lambda: self.screen.set_estado(
                        "Estado: no se pudo conectar a MongoDB",
                        "danger"
                    )
                )

                return

            # ==================================================
            # 1. ASISTENCIAS
            # ==================================================

            registros = obtener_registros(ip)

            documentos = []

            resumen_asistencias = {
                "insertados": 0,
                "actualizados": 0,
                "total": 0
            }

            if registros:

                documentos = consolidar_registros_por_dia(
                    registros=registros,
                    sede_id=sede_id,
                    origen="zkteco"
                )

                if documentos:

                    resumen_asistencias = (
                        guardar_asistencias_consolidadas(
                            cliente,
                            documentos
                        )
                    )

                    guardar_respaldo_manual(
                        documentos=documentos,
                        sede=sede_id,
                        checador_ip=ip,
                        resumen=resumen_asistencias
                    )

                else:

                    print(
                        "[INFO] Se encontraron registros "
                        "pero no se pudieron consolidar "
                        "documentos validos."
                    )

            else:

                # IMPORTANTE:
                # Ya NO hacemos return.
                # Aunque no haya asistencias,
                # continuamos sincronizando trabajadores.
                print(
                    "[INFO] No hay registros de asistencia. "
                    "Se continuara con la sincronizacion "
                    "de trabajadores."
                )

            # ==================================================
            # 2. TRABAJADORES
            # ==================================================

            resumen_usuarios = (
                self.sincronizar_usuarios_checador(
                    cliente=cliente,
                    ip=ip,
                    sede_id=sede_id,
                    agregar=True,
                    eliminar=True
                )
            )

            # ==================================================
            # RESULTADO
            # ==================================================

            self.screen.window.after(
                0,
                lambda: self.screen.set_estado(
                    f"Estado: sincronizacion {modo} completada | "
                    f"docs: {len(documentos)} | "
                    f"ins: {resumen_asistencias['insertados']} | "
                    f"act: {resumen_asistencias['actualizados']} | "
                    f"usuarios +{resumen_usuarios['agregados']} "
                    f"-{resumen_usuarios['eliminados']}",
                    "success"
                )
            )

            print(
                f"[OK] Sincronizacion {modo} completada"
            )

            print(
                f"[INFO] Registros leidos: "
                f"{len(registros) if registros else 0}"
            )

            print(
                f"[INFO] Documentos consolidados: "
                f"{len(documentos)}"
            )

            print(
                f"[INFO] Insertados: "
                f"{resumen_asistencias['insertados']}"
            )

            print(
                f"[INFO] Actualizados: "
                f"{resumen_asistencias['actualizados']}"
            )

            print(
                f"[INFO] Usuarios agregados: "
                f"{resumen_usuarios['agregados']}"
            )

            print(
                f"[INFO] Usuarios eliminados: "
                f"{resumen_usuarios['eliminados']}"
            )

        except Exception as e:

            error_msg = str(e)

            print(
                f"[ERROR] Error en sincronizacion "
                f"completa: {error_msg}"
            )

            self.screen.window.after(
                0,
                lambda: self.screen.set_estado(
                    f"Estado: error en sincronizacion: "
                    f"{error_msg}",
                    "danger"
                )
            )

        finally:

            self.sync_en_proceso = False

            self.screen.window.after(
                0,
                self._detener_animacion_sync
            )

    # ==========================================================
    # RECONFIGURAR
    # ==========================================================

    def reconfigurar(self):

        confirmar = messagebox.askyesno(
            "Reconfigurar",
            "Se eliminara la configuracion actual y el sistema "
            "volvera al inicio.\n\n"
            "Deseas continuar?"
        )

        if not confirmar:
            return

        ok = eliminar_configuracion()

        if ok:

            self.screen.set_estado(
                "Estado: configuracion eliminada. Reiniciando...",
                "success"
            )

            self.screen.window.after(
                600,
                self._reiniciar
            )

        else:

            self.screen.set_estado(
                "Estado: no se pudo eliminar la configuracion",
                "danger"
            )

    def _reiniciar(self):

        self.screen.window.destroy()
        reiniciar_aplicacion()

    # ==========================================================
    # AUTO SYNC
    # ==========================================================

    def activar_auto_sync(self):

        if self.auto_sync_activa:

            self.screen.set_estado(
                "Estado: la auto sincronizacion ya esta activa",
                "muted"
            )

            return

        self.auto_sync_activa = True

        self.screen.set_estado_auto_sync(
            "Auto sync: ACTIVADA cada 10 minutos",
            "success"
        )

        self.screen.set_estado(
            "Estado: auto sincronizacion activada",
            "success"
        )

        print(
            "[AUTO] Auto sincronizacion ACTIVADA"
        )

        # ------------------------------------------
        # SINCRONIZACION COMPLETA INMEDIATA
        # ------------------------------------------

        self._iniciar_tarea_sync(
            "Estado: sincronizacion automatica",
            self._ejecutar_sincronizacion_completa,
            "automatica"
        )

        # ------------------------------------------
        # PROGRAMAR SIGUIENTE
        # ------------------------------------------

        self._programar_siguiente_auto_sync()

    def desactivar_auto_sync(self):

        self.auto_sync_activa = False
        self.proxima_sync_dt = None

        if self.auto_sync_job is not None:

            try:
                self.screen.window.after_cancel(
                    self.auto_sync_job
                )

            except Exception:
                pass

            self.auto_sync_job = None

        self.screen.set_estado_auto_sync(
            "Auto sync: DESACTIVADA",
            "muted"
        )

        self.screen.set_proxima_sync(
            "Proxima ejecucion: no programada",
            "muted"
        )

        self.screen.set_estado(
            "Estado: auto sincronizacion desactivada",
            "muted"
        )

        print(
            "[AUTO] Auto sincronizacion DESACTIVADA"
        )

    def _ejecutar_auto_sync(self):

        if not self.auto_sync_activa:
            return

        print(
            "[AUTO] Ejecutando sincronizacion automatica..."
        )

        # ------------------------------------------
        # LA AUTOMATICA YA NO LLAMA AL MENU MANUAL
        # ------------------------------------------

        self._iniciar_tarea_sync(
            "Estado: sincronizacion automatica",
            self._ejecutar_sincronizacion_completa,
            "automatica"
        )

        if self.auto_sync_activa:
            self._programar_siguiente_auto_sync()

    # ==========================================================
    # PROGRAMACION AUTO SYNC
    # ==========================================================

    def _actualizar_indicador_proxima_sync(self):

        if (
            not self.auto_sync_activa
            or not self.proxima_sync_dt
        ):

            self.screen.set_proxima_sync(
                "Proxima ejecucion: no programada",
                "muted"
            )

            return

        hora = self.proxima_sync_dt.strftime(
            "%H:%M:%S"
        )

        self.screen.set_proxima_sync(
            f"Proxima ejecucion: {hora}",
            "success"
        )

    def _programar_siguiente_auto_sync(self):

        self.proxima_sync_dt = (
            datetime.now()
            + timedelta(
                milliseconds=self.auto_sync_intervalo
            )
        )

        self._actualizar_indicador_proxima_sync()

        self.auto_sync_job = (
            self.screen.window.after(
                self.auto_sync_intervalo,
                self._ejecutar_auto_sync
            )
        )

    # ==========================================================
    # ANIMACION
    # ==========================================================

    def _iniciar_animacion_sync(
        self,
        texto_base
    ):

        self.animacion_sync_activa = True

        self.screen.mostrar_progreso()

        self._actualizar_animacion_sync(
            texto_base,
            0
        )

        if hasattr(
            self.screen,
            "btn_sync_manual"
        ):
            self.screen.btn_sync_manual.config(
                state="disabled"
            )

        if hasattr(
            self.screen,
            "btn_auto_on"
        ):
            self.screen.btn_auto_on.config(
                state="disabled"
            )

    def _actualizar_animacion_sync(
        self,
        texto_base,
        paso
    ):

        if not self.animacion_sync_activa:
            return

        puntos = "." * (
            (paso % 3) + 1
        )

        self.screen.set_estado(
            f"{texto_base}{puntos}",
            "muted"
        )

        self.animacion_sync_job = (
            self.screen.window.after(
                500,
                lambda: self._actualizar_animacion_sync(
                    texto_base,
                    paso + 1
                )
            )
        )

    def _detener_animacion_sync(self):

        self.animacion_sync_activa = False

        if self.animacion_sync_job is not None:

            try:

                self.screen.window.after_cancel(
                    self.animacion_sync_job
                )

            except Exception:
                pass

            self.animacion_sync_job = None

        self.screen.ocultar_progreso()

        if hasattr(
            self.screen,
            "btn_sync_manual"
        ):
            self.screen.btn_sync_manual.config(
                state="normal"
            )

        if hasattr(
            self.screen,
            "btn_auto_on"
        ):
            self.screen.btn_auto_on.config(
                state="normal"
            )

    # ==========================================================
    # LIMPIAR REGISTROS DEL CHECADOR
    # ==========================================================

    def limpiar_checador(self):

        if self.sync_en_proceso:

            self.screen.set_estado(
                "Estado: no se puede limpiar mientras "
                "hay una sincronizacion en curso",
                "danger"
            )

            return

        confirmar = messagebox.askyesno(
            "Limpiar checador",
            "Se eliminaran TODOS los registros "
            "de asistencia del checador.\n\n"
            "Deseas continuar?"
        )

        if not confirmar:
            return

        ip = self.config_data.get(
            "checador_ip"
        )

        if not ip:

            self.screen.set_estado(
                "Estado: IP del checador no disponible",
                "danger"
            )

            return

        self.screen.set_estado(
            "Estado: limpiando checador...",
            "muted"
        )

        def tarea():

            try:

                resultado = (
                    limpiar_registros_asistencia(
                        ip
                    )
                )

                if resultado:

                    msg = (
                        "Estado: limpieza del "
                        "checador completada"
                    )

                    tipo = "success"

                else:

                    msg = (
                        "Estado: error al limpiar "
                        "el checador"
                    )

                    tipo = "danger"

                self.screen.window.after(
                    0,
                    lambda: self.screen.set_estado(
                        msg,
                        tipo
                    )
                )

                print(
                    f"[INFO] Limpieza manual checador: "
                    f"{'OK' if resultado else 'FALLO'}"
                )

            except Exception as e:

                error_msg = str(e)

                self.screen.window.after(
                    0,
                    lambda: self.screen.set_estado(
                        f"Estado: error al limpiar: "
                        f"{error_msg}",
                        "danger"
                    )
                )

                print(
                    f"[ERROR] Error en limpieza "
                    f"manual: {error_msg}"
                )

        threading.Thread(
            target=tarea,
            daemon=True
        ).start()

    # ==========================================================
    # SINCRONIZAR USUARIOS DEL CHECADOR
    # ==========================================================

    def sincronizar_usuarios_checador(
        self,
        cliente,
        ip,
        sede_id,
        agregar=True,
        eliminar=True
    ):
        """
        Sincroniza usuarios del checador con Mongo.

        agregar=True:
            Agrega trabajadores de Mongo
            que falten en el checador.

        eliminar=True:
            Elimina trabajadores sobrantes
            respetando las reglas de seguridad.

        Protecciones:
            - IDs <= 100 NO se eliminan
            - Administradores NO se eliminan
            - IDs no numericos NO se eliminan
        """

        # ------------------------------------------
        # OBTENER PERSONAL DE MONGO
        # ------------------------------------------

        trabajadores_mongo = (
            obtener_trabajadores_activos_por_sede(
                cliente,
                sede_id
            )
        )

        # ------------------------------------------
        # OBTENER PERSONAL DEL CHECADOR
        # ------------------------------------------

        usuarios_actuales = (
            obtener_usuarios_checador(
                ip
            )
        )

        # ------------------------------------------
        # MAPAS POR ID
        # ------------------------------------------

        mongo_por_id = {
            t["id_checador"]: t
            for t in trabajadores_mongo
        }

        checador_por_id = {
            u["user_id"]: u
            for u in usuarios_actuales
            if u.get("user_id")
        }

        agregados = 0
        eliminados = 0
        ignorados = 0
        errores = 0

        # ==================================================
        # AGREGAR TRABAJADORES FALTANTES
        # ==================================================

        if agregar:

            print(
                "[INFO] Buscando trabajadores "
                "faltantes en el checador..."
            )

            for id_checador, trabajador in mongo_por_id.items():

                if id_checador in checador_por_id:
                    continue

                uid_nuevo = (
                    obtener_siguiente_uid_disponible(
                        usuarios_actuales
                    )
                )

                # --------------------------------------
                # SIMULACION
                # --------------------------------------

                if self.modo_simulacion_usuarios:

                    print(
                        f"[SIMULACION] Se agregaria usuario "
                        f"{id_checador} - "
                        f"{trabajador['nombre']}"
                    )

                    agregados += 1

                    usuario_nuevo = {
                        "uid": uid_nuevo,
                        "user_id": id_checador,
                        "name": trabajador["nombre"],
                        "privilege": 0,
                        "es_admin": False
                    }

                    usuarios_actuales.append(
                        usuario_nuevo
                    )

                    checador_por_id[
                        id_checador
                    ] = usuario_nuevo

                # --------------------------------------
                # REAL
                # --------------------------------------

                else:

                    ok = agregar_usuario_checador(
                        ip=ip,
                        uid=uid_nuevo,
                        user_id=id_checador,
                        nombre=trabajador["nombre"],
                        privilege=0
                    )

                    if ok:

                        agregados += 1

                        usuario_nuevo = {
                            "uid": uid_nuevo,
                            "user_id": id_checador,
                            "name": trabajador["nombre"],
                            "privilege": 0,
                            "es_admin": False
                        }

                        usuarios_actuales.append(
                            usuario_nuevo
                        )

                        checador_por_id[
                            id_checador
                        ] = usuario_nuevo

                        print(
                            f"[OK] Usuario agregado: "
                            f"{id_checador} - "
                            f"{trabajador['nombre']}"
                        )

                    else:

                        errores += 1

                        print(
                            f"[ERROR] No se pudo agregar "
                            f"usuario {id_checador}"
                        )

        # ==================================================
        # ELIMINAR TRABAJADORES SOBRANTES
        # ==================================================

        if eliminar:

            print(
                "[INFO] Buscando trabajadores "
                "fuera de la sede..."
            )

            for user_id, usuario in list(
                checador_por_id.items()
            ):

                # --------------------------------------
                # EXISTE EN MONGO PARA ESTA SEDE
                # --------------------------------------

                if user_id in mongo_por_id:
                    continue

                # --------------------------------------
                # VALIDAR ID NUMERICO
                # --------------------------------------

                try:

                    id_num = int(
                        user_id
                    )

                except (
                    ValueError,
                    TypeError
                ):

                    ignorados += 1

                    print(
                        f"[INFO] Usuario ignorado por "
                        f"user_id no numerico: "
                        f"{user_id}"
                    )

                    continue

                # --------------------------------------
                # PROTEGER IDS <= 100
                # --------------------------------------

                if id_num <= 100:

                    ignorados += 1

                    print(
                        f"[INFO] Usuario protegido por "
                        f"id <= 100: {user_id}"
                    )

                    continue

                # --------------------------------------
                # PROTEGER ADMINISTRADORES
                # --------------------------------------

                if usuario.get(
                    "es_admin"
                ):

                    ignorados += 1

                    print(
                        f"[INFO] Usuario protegido por "
                        f"privilegio admin: {user_id}"
                    )

                    continue

                # --------------------------------------
                # OBTENER UID
                # --------------------------------------

                uid = usuario.get(
                    "uid"
                )

                if uid is None:

                    errores += 1

                    print(
                        f"[WARN] No se pudo eliminar "
                        f"user_id={user_id} "
                        f"porque no tiene uid"
                    )

                    continue

                # --------------------------------------
                # SIMULACION
                # --------------------------------------

                if self.modo_simulacion_usuarios:

                    print(
                        f"[SIMULACION] Se eliminaria "
                        f"usuario {user_id}"
                    )

                    eliminados += 1

                # --------------------------------------
                # REAL
                # --------------------------------------

                else:

                    ok = (
                        eliminar_usuario_checador(
                            ip,
                            uid
                        )
                    )

                    if ok:

                        eliminados += 1

                        print(
                            f"[OK] Usuario eliminado "
                            f"del checador: {user_id}"
                        )

                    else:

                        errores += 1

                        print(
                            f"[ERROR] No se pudo eliminar "
                            f"usuario {user_id}"
                        )

        # ==================================================
        # RESUMEN
        # ==================================================

        resumen = {
            "agregados": agregados,
            "eliminados": eliminados,
            "ignorados": ignorados,
            "errores": errores,
            "total_mongo": len(
                trabajadores_mongo
            ),
            "total_checador": len(
                usuarios_actuales
            )
        }

        print(
            "[INFO] Resumen sincronizacion "
            f"usuarios checador: {resumen}"
        )

        return resumen

    # ==========================================================
    # SALIR
    # ==========================================================

    def salir(self):

        self.auto_sync_activa = False

        if self.auto_sync_job is not None:

            try:

                self.screen.window.after_cancel(
                    self.auto_sync_job
                )

            except Exception:
                pass

            self.auto_sync_job = None

        self.screen.window.destroy()