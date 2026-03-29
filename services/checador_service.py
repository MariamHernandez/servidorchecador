import socket
import time
from zk import ZK


def buscar_checador(progress_callback=None, stop_event=None):
    puerto = 4370

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
            return None, []

        mensaje = f"Escaneando {ip}..."
        if progress_callback:
            progress_callback(idx, total, mensaje)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.6)

        try:
            resultado = sock.connect_ex((ip, puerto))

            if resultado == 0:
                usuarios = conectar_checador_y_usuarios(ip)

                if usuarios is not None:
                    return ip, usuarios

        except Exception:
            pass
        finally:
            sock.close()

        time.sleep(0.1)

    return None, []


def conectar_checador_y_usuarios(ip):
    intentos = [
        {"timeout": 5, "ommit_ping": True},
        {"timeout": 8, "ommit_ping": True},
        {"timeout": 10, "ommit_ping": True},
        {"timeout": 8, "force_udp": True, "ommit_ping": True},
    ]

    for config in intentos:
        conexion = None
        try:
            print(f"🔎 Probando conexión con {ip} usando {config}")

            zk = ZK(
                ip,
                port=4370,
                **config
            )

            conexion = zk.connect()
            usuarios = conexion.get_users()

            print(f"✅ Conexión real exitosa con {ip}")
            return normalizar_usuarios(usuarios)

        except Exception as e:
            print(f"❌ Error al conectar con checador {ip} con {config}: {e}")

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
            "user_id": str(getattr(usuario, "user_id", "")),
            "name": getattr(usuario, "name", "") or ""
        }
        for usuario in usuarios
    ]