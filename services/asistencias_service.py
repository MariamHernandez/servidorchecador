from collections import defaultdict
from datetime import datetime


def _obtener_user_id(registro):
    """
    Intenta extraer el user_id del registro del checador.
    """
    user_id = getattr(registro, "user_id", None)

    if user_id is None:
        user_id = getattr(registro, "uid", None)

    if user_id is None:
        return None

    return str(user_id).strip()


def _obtener_timestamp(registro):
    """
    Intenta extraer el timestamp del registro del checador.
    """
    timestamp = getattr(registro, "timestamp", None)

    if not timestamp:
        return None

    return timestamp


def consolidar_registros_por_dia(registros, sede_id, origen="zkteco"):
    """
    Convierte registros crudos del checador en documentos consolidados por:
    - trabajador
    - sede
    - fecha

    NO interpreta entrada/salida.
    Solo conserva:
    - primerRegistro
    - ultimoRegistro
    - totalRegistros
    - registros completos
    """

    agrupados = defaultdict(list)

    for registro in registros:
        trabajador = _obtener_user_id(registro)
        timestamp = _obtener_timestamp(registro)

        if not trabajador or not timestamp:
            continue

        fecha = timestamp.strftime("%Y-%m-%d")
        key = (trabajador, sede_id, fecha)
        agrupados[key].append(timestamp)

    documentos = []
    ahora = datetime.now().isoformat()

    for (trabajador, sede_id, fecha), timestamps in agrupados.items():
        timestamps_ordenados = sorted(timestamps)

        primer = timestamps_ordenados[0]
        ultimo = timestamps_ordenados[-1]

        documento = {
            "trabajador": trabajador,
            "sede": sede_id,
            "fecha": fecha,
            "primerRegistro": {
                "fechaHora": primer.isoformat()
            },
            "ultimoRegistro": {
                "fechaHora": ultimo.isoformat()
            },
            "totalRegistros": len(timestamps_ordenados),
            "registros": [
                {"fechaHora": ts.isoformat()}
                for ts in timestamps_ordenados
            ],
            "ultimaSincronizacion": ahora,
            "origen": origen
        }

        documentos.append(documento)

    return documentos