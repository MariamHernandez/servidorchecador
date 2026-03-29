from collections import Counter, defaultdict


def detectar_sede_por_checador(usuarios_checador, trabajadores_mongo, umbral_minimo=30):
    """
    Detecta la sede más probable comparando IDs de usuarios del checador
    contra los trabajadores registrados en MongoDB.

    Retorna un dict con:
    - decision: "auto" o "manual"
    - sede
    - porcentaje
    - known_ids
    - total_ids
    - top3
    """

    if not usuarios_checador or not trabajadores_mongo:
        return {
            "decision": "manual",
            "known_ids": 0,
            "total_ids": len(usuarios_checador) if usuarios_checador else 0,
            "top3": []
        }

    # =============================
    # Índice de trabajadores por id_checador
    # =============================
    indice_trabajadores = {}

    for trabajador in trabajadores_mongo:
        id_checador = str(trabajador.get("id_checador", "")).strip()
        sede = trabajador.get("sede")

        if id_checador and sede is not None:
            indice_trabajadores[id_checador] = sede

    # =============================
    # Comparar usuarios del checador contra Mongo
    # =============================
    coincidencias_por_sede = Counter()
    known_ids = 0

    for usuario in usuarios_checador:
        user_id = str(usuario.get("user_id", "")).strip()

        if not user_id:
            continue

        sede = indice_trabajadores.get(user_id)
        if sede is not None:
            coincidencias_por_sede[sede] += 1
            known_ids += 1

    total_ids = len(usuarios_checador)

    if known_ids == 0 or not coincidencias_por_sede:
        return {
            "decision": "manual",
            "known_ids": 0,
            "total_ids": total_ids,
            "top3": []
        }

    top_sedes = coincidencias_por_sede.most_common(3)
    sede_ganadora, coincidencias_ganadora = top_sedes[0]
    porcentaje = (coincidencias_ganadora / total_ids) * 100 if total_ids > 0 else 0

    top3 = [
        {
            "sede": sede,
            "coincidencias": coincidencias
        }
        for sede, coincidencias in top_sedes
    ]

    if porcentaje >= umbral_minimo:
        return {
            "decision": "auto",
            "sede": sede_ganadora,
            "porcentaje": porcentaje,
            "known_ids": known_ids,
            "total_ids": total_ids,
            "top3": top3
        }

    return {
        "decision": "manual",
        "known_ids": known_ids,
        "total_ids": total_ids,
        "top3": top3
    }