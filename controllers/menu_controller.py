import threading
from tkinter import messagebox
from datetime import datetime, timedelta

from ui.screens.menu_screen import MenuScreen
from services.config_service import cargar_configuracion, eliminar_configuracion
from services.navigation_service import reiniciar_aplicacion
from services.mongo_service import conectar_mongo, guardar_asistencias_consolidadas, obtener_trabajadores_activos_por_sede
from services.checador_service import obtener_registros, limpiar_registros_asistencia, obtener_usuarios_checador, agregar_usuario_checador, eliminar_usuario_checador, obtener_siguiente_uid_disponible
from services.asistencias_service import consolidar_registros_por_dia
from services.respaldo_service import guardar_respaldo_manual

class MenuController:
    def __init__(self):
        self.config_data = cargar_configuracion() or {}
        self.auto_sync_activa = False
        self.auto_sync_intervalo = 10 * 60 * 1000  # 10 minutos en milisegundos
        self.auto_sync_job = None
        self.sync_en_proceso = False
        self.animacion_sync_activa = False
        self.animacion_sync_job = None
        self.proxima_sync_dt = None
        self.modo_simulacion_usuarios = False
        
        self.screen = MenuScreen(
            on_sincronizacion_manual_callback=self.sincronizacion_manual,
            on_iniciar_auto_sync_callback=self.activar_auto_sync,
            on_detener_auto_sync_callback=self.desactivar_auto_sync,
            on_limpiar_callback=self.limpiar_checador,
            on_reconfigurar_callback=self.reconfigurar,
            on_salir_callback=self.salir,
            config_data=self.config_data
        )

        self.screen.window.protocol("WM_DELETE_WINDOW", self.salir)

    def iniciar(self):
        self.screen.iniciar()

    def _get_cliente_mongo(self):
        cliente, _ = conectar_mongo()
        return cliente

    def sincronizacion_manual(self):
        if self.sync_en_proceso:
            self.screen.set_estado("Estado: ya hay una sincronizacion en proceso...", "muted")
            return

        self.sync_en_proceso = True

        # 🔥 Animación bonita
        self._iniciar_animacion_sync("Estado: sincronizando asistencias")

        # 🔥 Ejecutar en hilo (NO bloquea la interfaz)
        hilo = threading.Thread(target=self._ejecutar_sincronizacion_manual, daemon=True)
        hilo.start()
        
    def reconfigurar(self):
        confirmar = messagebox.askyesno(
            "Reconfigurar",
            "Se eliminara la configuracion actual y el sistema volvera al inicio.\n\nDeseas continuar?"
        )

        if not confirmar:
            return

        ok = eliminar_configuracion()

        if ok:
            self.screen.set_estado("Estado: configuracion eliminada. Reiniciando...", "success")
            self.screen.window.after(600, self._reiniciar)
        else:
            self.screen.set_estado("Estado: no se pudo eliminar la configuracion", "danger")

    def _reiniciar(self):
        self.screen.window.destroy()
        reiniciar_aplicacion()

    def activar_auto_sync(self):
        if self.auto_sync_activa:
            self.screen.set_estado("Estado: la auto sincronización ya está activa", "muted")
            return

        self.auto_sync_activa = True
        self.screen.set_estado_auto_sync("Auto sync: ACTIVADA cada 10 minutos", "success")
        self.screen.set_estado("Estado: auto sincronización activada", "success")
        print("[AUTO] Auto sincronización ACTIVADA")

        # ejecuta una sincronización inmediata
        self.sincronizacion_manual()

        # programa la siguiente
        self._programar_siguiente_auto_sync()

    def desactivar_auto_sync(self):
        self.auto_sync_activa = False
        self.proxima_sync_dt = None

        if self.auto_sync_job is not None:
            try:
                self.screen.window.after_cancel(self.auto_sync_job)
            except Exception:
                pass
            self.auto_sync_job = None

        self.screen.set_estado_auto_sync("Auto sync: DESACTIVADA", "muted")
        self.screen.set_proxima_sync("Próxima ejecución: no programada", "muted")
        self.screen.set_estado("Estado: auto sincronización desactivada", "muted")
        print("[AUTO] Auto sincronización DESACTIVADA")

    def _ejecutar_auto_sync(self):
        if not self.auto_sync_activa:
            return

        print("[AUTO] Ejecutando sincronización automática...")
        self.sincronizacion_manual()

        if self.auto_sync_activa:
            self._programar_siguiente_auto_sync()

    def _ejecutar_sincronizacion_manual(self):
        try:
            ip = self.config_data.get("checador_ip")
            sede_id = self.config_data.get("sede")

            if not ip or sede_id is None:
                self.screen.window.after(
                    0,
                    lambda: self.screen.set_estado("Estado: configuracion incompleta", "danger")
                )
                return

            cliente = self._get_cliente_mongo()
            if not cliente:
                self.screen.window.after(
                    0,
                    lambda: self.screen.set_estado("Estado: no se pudo conectar a MongoDB", "danger")
                )
                return

            registros = obtener_registros(ip)

            if not registros:
                self.screen.window.after(
                    0,
                    lambda: self.screen.set_estado("Estado: no se encontraron registros en el checador", "muted")
                )
                return

            documentos = consolidar_registros_por_dia(
                registros=registros,
                sede_id=sede_id,
                origen="zkteco"
            )

            if not documentos:
                self.screen.window.after(
                    0,
                    lambda: self.screen.set_estado("Estado: no se pudieron consolidar registros validos", "danger")
                )
                return

            resumen = guardar_asistencias_consolidadas(cliente, documentos)

            ruta_respaldo = guardar_respaldo_manual(
                documentos=documentos,
                sede=sede_id,
                checador_ip=ip,
                resumen=resumen
            )

            resumen_usuarios = self.sincronizar_usuarios_checador(cliente, ip, sede_id)
            
            self.screen.window.after(
                0,
                lambda: self.screen.set_estado(
                    f"Estado: sincronizacion completada | docs: {len(documentos)} | ins: {resumen['insertados']} | act: {resumen['actualizados']} | usuarios +{resumen_usuarios['agregados']} -{resumen_usuarios['eliminados']}",
                    "success"
                )
            )

            print("[OK] Sincronizacion manual completada")
            print(f"[INFO] Registros leidos del checador: {len(registros)}")
            print(f"[INFO] Documentos consolidados: {len(documentos)}")
            print(f"[INFO] Respaldo guardado en: {ruta_respaldo}")
            print(f"[INFO] Insertados: {resumen['insertados']}")
            print(f"[INFO] Actualizados: {resumen['actualizados']}")
            print(f"[INFO] Total procesados: {resumen['total']}")
            
        except Exception as e:
            error_msg = str(e)

            print(f"[ERROR] Error en sincronizacion manual: {error_msg}")

            self.screen.window.after(
                0,
                lambda: self.screen.set_estado(f"Estado: error en sincronizacion: {error_msg}", "danger")
            )

        finally:
            self.sync_en_proceso = False
            self.screen.window.after(0, self._detener_animacion_sync)

    def _iniciar_animacion_sync(self, texto_base):
        self.animacion_sync_activa = True
        self.screen.mostrar_progreso()
        self._actualizar_animacion_sync(texto_base, 0)

        if hasattr(self.screen, "btn_sync_manual"):
            self.screen.btn_sync_manual.config(state="disabled")

        if hasattr(self.screen, "btn_auto_on"):
            self.screen.btn_auto_on.config(state="disabled")

    def _actualizar_animacion_sync(self, texto_base, paso):
        if not self.animacion_sync_activa:
            return

        puntos = "." * ((paso % 3) + 1)
        self.screen.set_estado(f"{texto_base}{puntos}", "muted")

        self.animacion_sync_job = self.screen.window.after(
            500,
            lambda: self._actualizar_animacion_sync(texto_base, paso + 1)
        )

    def _actualizar_indicador_proxima_sync(self):
        if not self.auto_sync_activa or not self.proxima_sync_dt:
            self.screen.set_proxima_sync("Próxima ejecución: no programada", "muted")
            return

        hora = self.proxima_sync_dt.strftime("%H:%M:%S")
        self.screen.set_proxima_sync(f"Próxima ejecución: {hora}", "success")

    def _programar_siguiente_auto_sync(self):
        self.proxima_sync_dt = datetime.now() + timedelta(milliseconds=self.auto_sync_intervalo)
        self._actualizar_indicador_proxima_sync()

        self.auto_sync_job = self.screen.window.after(
            self.auto_sync_intervalo,
            self._ejecutar_auto_sync
        )

    def _detener_animacion_sync(self):
        self.animacion_sync_activa = False

        if self.animacion_sync_job is not None:
            try:
                self.screen.window.after_cancel(self.animacion_sync_job)
            except Exception:
                pass
            self.animacion_sync_job = None

        self.screen.ocultar_progreso()

        if hasattr(self.screen, "btn_sync_manual"):
            self.screen.btn_sync_manual.config(state="normal")

        if hasattr(self.screen, "btn_auto_on"):
            self.screen.btn_auto_on.config(state="normal")

    def limpiar_checador(self):
        if self.sync_en_proceso:
            self.screen.set_estado("Estado: no se puede limpiar mientras hay una sincronizacion en curso", "danger")
            return

        confirmar = messagebox.askyesno(
            "Limpiar checador",
            "Se eliminaran TODOS los registros de asistencia del checador.\n\n¿Deseas continuar?"
        )

        if not confirmar:
            return

        ip = self.config_data.get("checador_ip")

        if not ip:
            self.screen.set_estado("Estado: IP del checador no disponible", "danger")
            return

        self.screen.set_estado("Estado: limpiando checador...", "muted")

        def tarea():
            try:
                resultado = limpiar_registros_asistencia(ip)

                if resultado:
                    msg = "Estado: limpieza del checador completada"
                    tipo = "success"
                else:
                    msg = "Estado: error al limpiar el checador"
                    tipo = "danger"

                self.screen.window.after(
                    0,
                    lambda: self.screen.set_estado(msg, tipo)
                )

                print(f"[INFO] Limpieza manual checador: {'OK' if resultado else 'FALLO'}")

            except Exception as e:
                error_msg = str(e)

                self.screen.window.after(
                    0,
                    lambda: self.screen.set_estado(f"Estado: error al limpiar: {error_msg}", "danger")
                )

                print(f"[ERROR] Error en limpieza manual: {error_msg}")

        threading.Thread(target=tarea, daemon=True).start()

    def sincronizar_usuarios_checador(self, cliente, ip, sede_id):
        """
        Sincroniza usuarios del checador con Mongo respetando reglas:
        - agregar faltantes de Mongo
        - eliminar sobrantes solo si id > 100 y no admin
        - ignorar ids <= 100 y administradores
        """
        trabajadores_mongo = obtener_trabajadores_activos_por_sede(cliente, sede_id)
        usuarios_actuales = obtener_usuarios_checador(ip)

        mongo_por_id = {t["id_checador"]: t for t in trabajadores_mongo}
        checador_por_id = {u["user_id"]: u for u in usuarios_actuales if u.get("user_id")}

        agregados = 0
        eliminados = 0
        ignorados = 0
        errores = 0

        # Agregar trabajadores faltantes en checador
        for id_checador, trabajador in mongo_por_id.items():
            if id_checador not in checador_por_id:
                uid_nuevo = obtener_siguiente_uid_disponible(usuarios_actuales)

                if self.modo_simulacion_usuarios:
                    print(f"[SIMULACION] Se agregaria usuario {id_checador} - {trabajador['nombre']}")
                    agregados += 1

                    usuarios_actuales.append({
                        "uid": uid_nuevo,
                        "user_id": id_checador,
                        "name": trabajador["nombre"],
                        "privilege": 0,
                        "es_admin": False
                    })
                    checador_por_id[id_checador] = usuarios_actuales[-1]
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
                        usuarios_actuales.append({
                            "uid": uid_nuevo,
                            "user_id": id_checador,
                            "name": trabajador["nombre"],
                            "privilege": 0,
                            "es_admin": False
                        })
                        checador_por_id[id_checador] = usuarios_actuales[-1]
                    else:
                        errores += 1

        # Eliminar usuarios sobrantes con reglas de seguridad
        for user_id, usuario in checador_por_id.items():
            if user_id in mongo_por_id:
                continue

            try:
                id_num = int(user_id)
            except ValueError:
                ignorados += 1
                print(f"[INFO] Usuario ignorado por user_id no numérico: {user_id}")
                continue

            if id_num <= 100:
                ignorados += 1
                print(f"[INFO] Usuario protegido por id <= 100: {user_id}")
                continue

            if usuario.get("es_admin"):
                ignorados += 1
                print(f"[INFO] Usuario protegido por privilegio admin: {user_id}")
                continue

            uid = usuario.get("uid")
            if uid is None:
                errores += 1
                print(f"[WARN] No se pudo eliminar user_id={user_id} porque no tiene uid")
                continue

            if self.modo_simulacion_usuarios:
                print(f"[SIMULACION] Se eliminaria usuario {user_id}")
                eliminados += 1
            else:
                ok = eliminar_usuario_checador(ip, uid)

                if ok:
                    eliminados += 1
                else:
                    errores += 1

        resumen = {
            "agregados": agregados,
            "eliminados": eliminados,
            "ignorados": ignorados,
            "errores": errores,
            "total_mongo": len(trabajadores_mongo),
            "total_checador": len(usuarios_actuales)
        }

        print(f"[INFO] Resumen sincronización usuarios checador: {resumen}")
        return resumen

    def salir(self):
        self.auto_sync_activa = False

        if self.auto_sync_job is not None:
            try:
                self.screen.window.after_cancel(self.auto_sync_job)
            except Exception:
                pass
            self.auto_sync_job = None

        self.screen.window.destroy()