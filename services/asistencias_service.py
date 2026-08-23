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

    Mantiene el formato nuevo:
    - primerRegistro
    - ultimoRegistro
    - totalRegistros
    - registros completos

    Ademas genera detalle[] como capa de compatibilidad
    con el backend actual:
    - primera marca = Entrada
    - ultima marca = Salida, solamente si hay mas de una marca

    Python NO calcula:
    - faltas
    - retardos
    - permisos
    - vacaciones
    - descansos
    - eventos
    - estados laborales

    Esa logica sigue siendo responsabilidad del backend.
    """

    agrupados = defaultdict(list)

    # ==========================================================
    # AGRUPAR REGISTROS POR TRABAJADOR + SEDE + FECHA
    # ==========================================================

    for registro in registros:

        trabajador = _obtener_user_id(registro)
        timestamp = _obtener_timestamp(registro)

        if not trabajador or not timestamp:
            continue

        fecha = timestamp.strftime("%Y-%m-%d")

        key = (
            trabajador,
            sede_id,
            fecha
        )

        agrupados[key].append(
            timestamp
        )

    # ==========================================================
    # CREAR DOCUMENTOS CONSOLIDADOS
    # ==========================================================

    documentos = []

    ahora = datetime.now().isoformat()

    for (
        trabajador,
        sede_id_actual,
        fecha
    ), timestamps in agrupados.items():

        # ------------------------------------------------------
        # ORDENAR TODAS LAS MARCAS DEL DIA
        # ------------------------------------------------------

        timestamps_ordenados = sorted(
            timestamps
        )

        primer = timestamps_ordenados[0]
        ultimo = timestamps_ordenados[-1]

        # ======================================================
        # FORMATO DE COMPATIBILIDAD PARA EL BACKEND
        # ======================================================

        detalle = []

        # ------------------------------------------------------
        # PRIMERA MARCA = ENTRADA
        # ------------------------------------------------------

        detalle.append({
            "tipo": "Entrada",
            "fechaHora": primer.isoformat(),
            "sede": sede_id_actual
        })

        # ------------------------------------------------------
        # ULTIMA MARCA = SALIDA
        #
        # Solo se agrega si existen 2 o mas registros.
        #
        # Si solamente existe una marca, NO inventamos salida.
        # ------------------------------------------------------

        if len(timestamps_ordenados) > 1:

            detalle.append({
                "tipo": "Salida",
                "fechaHora": ultimo.isoformat(),
                "sede": sede_id_actual
            })

        # ======================================================
        # DOCUMENTO FINAL
        # ======================================================

        documento = {
            "trabajador": trabajador,
            "sede": sede_id_actual,
            "fecha": fecha,

            # --------------------------------------------------
            # FORMATO NUEVO
            # --------------------------------------------------

            "primerRegistro": {
                "fechaHora": primer.isoformat()
            },

            "ultimoRegistro": {
                "fechaHora": ultimo.isoformat()
            },

            "totalRegistros": len(
                timestamps_ordenados
            ),

            "registros": [
                {
                    "fechaHora": ts.isoformat()
                }
                for ts in timestamps_ordenados
            ],

            # --------------------------------------------------
            # COMPATIBILIDAD CON BACKEND EXISTENTE
            # --------------------------------------------------

            "detalle": detalle,

            # --------------------------------------------------
            # METADATOS
            # --------------------------------------------------

            "ultimaSincronizacion": ahora,
            "origen": origen
        }

        documentos.append(
            documento
        )

    return documentos