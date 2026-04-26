import socket
import time
from zk import ZK

PUERTO_CHECADOR = 4370

def buscar_checador(progress_callback=None, stop_event=None):
    """
    Busca el checador en IPs prioritarias y luego en un rango local.
    Primero intenta conexión real con ZK, porque algunos dispositivos
    no responden bien al escaneo TCP rápido con socket.
    """
    ips_prioritarias = [
        "192.168.1.101",
    ]

    ips_rango = [f"192.168.1.{host}" for host in range(100, 111)]

    ips_a_probar = []
    for ip in ips_prioritarias + ips_rango:
        if ip not in ips_a_probar:
            ips_a_probar.append(ip)

    total = len(ips_a_probar)

    for idx, ip in enumerate(ips_a_probar, start=1):
        if stop_event and stop_event.is_set():
            print("[INFO] Búsqueda cancelada por stop_event")
            return None, []

        mensaje = f"Escaneando {ip}..."
        if progress_callback:
            progress_callback(idx, total, mensaje)

        print(f"[INFO] Intentando detectar checador en {ip}")

        usuarios = conectar_checador_y_usuarios(ip)
        if usuarios is not None:
            print(f"[OK] Checador encontrado en {ip}")
            return ip, usuarios

        if puerto_abierto(ip, PUERTO_CHECADOR, timeout=1.5):
            print(f"[WARN] El puerto {PUERTO_CHECADOR} respondió en {ip}, pero ZK no logró conectar")
        else:
            print(f"[INFO] Sin respuesta en puerto {PUERTO_CHECADOR} para {ip}")

        time.sleep(0.15)

    print("[ERROR] No se encontró ningún checador disponible")
    return None, []

def puerto_abierto(ip, puerto, timeout=1.5):
    """
    Verifica si el puerto TCP responde.
    No decide por sí solo si hay checador, solo sirve como apoyo de diagnóstico.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)

    try:
        resultado = sock.connect_ex((ip, puerto))
        return resultado == 0
    except Exception as e:
        print(f"[ERROR] Error al probar puerto {puerto} en {ip}: {e}")
        return False
    finally:
        sock.close()

def conectar_checador_y_usuarios(ip):
    """
    Intenta conexión real con el checador usando varias configuraciones.
    Si conecta, regresa los usuarios normalizados.
    Si no conecta, regresa None.
    """
    intentos = [
        {"timeout": 8, "ommit_ping": True},
        {"timeout": 10, "ommit_ping": True},
        {"timeout": 12, "ommit_ping": True},
        {"timeout": 8, "force_udp": True, "ommit_ping": True},
        {"timeout": 10, "force_udp": True, "ommit_ping": True},
    ]

    for config in intentos:
        conexion = None
        try:
            print(f"[INFO] Probando conexión ZK con {ip} usando {config}")

            zk = ZK(
                ip,
                port=PUERTO_CHECADOR,
                **config
            )

            conexion = zk.connect()
            usuarios = conexion.get_users()

            print(f"[OK] Conexión real exitosa con {ip}. Usuarios encontrados: {len(usuarios)}")
            return normalizar_usuarios(usuarios)

        except Exception as e:
            print(f"[ERROR] Falló conexión con checador {ip} usando {config}: {e}")

        finally:
            try:
                if conexion:
                    conexion.disconnect()
            except Exception:
                pass

    return None

def normalizar_usuarios(usuarios):
    return [
        {
            "uid": getattr(usuario, "uid", None),
            "user_id": str(getattr(usuario, "user_id", "")).strip(),
            "name": getattr(usuario, "name", "") or "",
            "privilege": getattr(usuario, "privilege", 0),
            "es_admin": getattr(usuario, "privilege", 0) != 0
        }
        for usuario in usuarios
    ]

def obtener_registros(ip):
    conexion = None

    intentos = [
        {"timeout": 8, "ommit_ping": True},
        {"timeout": 10, "ommit_ping": True},
        {"timeout": 8, "force_udp": True, "ommit_ping": True},
    ]

    for config in intentos:
        try:
            print(f"[INFO] Intentando obtener registros desde {ip} con {config}")

            zk = ZK(ip, port=PUERTO_CHECADOR, **config)
            conexion = zk.connect()

            registros = conexion.get_attendance()
            print(f"[OK] Registros obtenidos correctamente desde {ip}: {len(registros)}")
            return registros

        except Exception as e:
            print(f"[ERROR] Error al obtener registros del checador {ip} con {config}: {e}")

        finally:
            try:
                if conexion:
                    conexion.disconnect()
            except Exception:
                pass

        conexion = None

    return []

def obtener_usuarios_checador(ip):
    """
    Obtiene usuarios del checador con datos suficientes para decidir
    si se agregan, eliminan o se ignoran.
    """
    conexion = None

    intentos = [
        {"timeout": 8, "ommit_ping": True},
        {"timeout": 10, "ommit_ping": True},
        {"timeout": 8, "force_udp": True, "ommit_ping": True},
    ]

    for config in intentos:
        try:
            print(f"[INFO] Obteniendo usuarios del checador {ip} con {config}")

            zk = ZK(ip, port=PUERTO_CHECADOR, **config)
            conexion = zk.connect()

            usuarios = conexion.get_users()
            normalizados = []

            for usuario in usuarios:
                privilege = getattr(usuario, "privilege", 0)
                user_id = str(getattr(usuario, "user_id", "")).strip()

                normalizados.append({
                    "uid": getattr(usuario, "uid", None),
                    "user_id": user_id,
                    "name": getattr(usuario, "name", "") or "",
                    "privilege": privilege,
                    "es_admin": privilege != 0
                })

            print(f"[OK] Usuarios obtenidos correctamente desde {ip}: {len(normalizados)}")
            return normalizados

        except Exception as e:
            print(f"[ERROR] Error al obtener usuarios del checador {ip} con {config}: {e}")

        finally:
            try:
                if conexion:
                    conexion.disconnect()
            except Exception:
                pass

        conexion = None

    return []

def agregar_usuario_checador(ip, uid, user_id, nombre, privilege=0, password="", card=0):
    """
    Agrega un usuario al checador.
    """
    conexion = None

    intentos = [
        {"timeout": 8, "ommit_ping": True},
        {"timeout": 10, "ommit_ping": True},
        {"timeout": 8, "force_udp": True, "ommit_ping": True},
    ]

    for config in intentos:
        try:
            print(f"[INFO] Agregando usuario {user_id} al checador {ip} con {config}")

            zk = ZK(ip, port=PUERTO_CHECADOR, **config)
            conexion = zk.connect()

            conexion.set_user(
                uid=uid,
                name=nombre,
                privilege=privilege,
                password=password,
                group_id="",
                user_id=str(user_id),
                card=card
            )

            print(f"[OK] Usuario {user_id} agregado correctamente al checador")
            return True

        except Exception as e:
            print(f"[ERROR] Error al agregar usuario {user_id} al checador {ip} con {config}: {e}")

        finally:
            try:
                if conexion:
                    conexion.disconnect()
            except Exception:
                pass

        conexion = None

    return False

def eliminar_usuario_checador(ip, uid):
    """
    Elimina un usuario del checador por uid interno.
    """
    conexion = None

    intentos = [
        {"timeout": 8, "ommit_ping": True},
        {"timeout": 10, "ommit_ping": True},
        {"timeout": 8, "force_udp": True, "ommit_ping": True},
    ]

    for config in intentos:
        try:
            print(f"[INFO] Eliminando usuario uid={uid} del checador {ip} con {config}")

            zk = ZK(ip, port=PUERTO_CHECADOR, **config)
            conexion = zk.connect()

            conexion.delete_user(uid=uid)

            print(f"[OK] Usuario uid={uid} eliminado correctamente del checador")
            return True

        except Exception as e:
            print(f"[ERROR] Error al eliminar usuario uid={uid} del checador {ip} con {config}: {e}")

        finally:
            try:
                if conexion:
                    conexion.disconnect()
            except Exception:
                pass

        conexion = None

    return False

def obtener_siguiente_uid_disponible(usuarios):
    usados = set()

    for usuario in usuarios:
        uid = usuario.get("uid")
        if isinstance(uid, int):
            usados.add(uid)

    uid = 1
    while uid in usados:
        uid += 1

    return uid

def limpiar_registros_asistencia(ip):
    """
    Elimina los registros de asistencia del checador.
    NO elimina usuarios.
    Retorna True si la limpieza fue exitosa, False si falló.
    """
    conexion = None

    intentos = [
        {"timeout": 8, "ommit_ping": True},
        {"timeout": 10, "ommit_ping": True},
        {"timeout": 8, "force_udp": True, "ommit_ping": True},
    ]

    for config in intentos:
        try:
            print(f"[INFO] Intentando limpiar registros de asistencia en {ip} con {config}")

            zk = ZK(ip, port=PUERTO_CHECADOR, **config)
            conexion = zk.connect()

            conexion.clear_attendance()

            print(f"[OK] Registros de asistencia eliminados correctamente en {ip}")
            return True

        except Exception as e:
            print(f"[ERROR] Error al limpiar registros de asistencia en {ip} con {config}: {e}")

        finally:
            try:
                if conexion:
                    conexion.disconnect()
            except Exception:
                pass

        conexion = None

    return False