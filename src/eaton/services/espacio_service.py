# services/espacio_service.py

import pandas as pd


def _convertir_x(valor):

    texto = str(valor).upper().replace("X", "").strip()

    return float(texto)


def _convertir_corriente(valor):

    texto = str(valor).upper().replace("A", "").strip()

    if "-" in texto:
        texto = texto.split("-")[-1].strip()

    return int(float(texto))


def capacidad_de_conectores(capacidad):

    if capacidad == "600 AMP":
        return "1600 AMP"

    if capacidad in ["800 AMP", "1200 AMP"]:
        return "2000 AMP"

    return capacidad


def obtener_espacio_total(catalogo, capacidad, altura=None):

    if capacidad in ["600 AMP", "800 AMP", "1200 AMP"]:

        if altura is None:
            return 0

        return catalogo.obtener_espacio_por_capacidad_y_altura(
            capacidad,
            altura
        )

    return catalogo.obtener_espacio_por_capacidad(capacidad)


def obtener_x_para_breaker(catalogo, capacidad, producto):

    marco = producto.get("Marco")
    polos = int(float(producto["# Polos"]))
    corriente = _convertir_corriente(producto["Corriente"])
    clasificacion = producto.get("Clasificacion")

    if pd.isna(clasificacion):
        clasificacion = None

    kits = catalogo.obtener_kits_conectores_para_breaker(
        capacidad_de_conectores(capacidad),
        marco,
        polos,
        corriente,
        clasificacion
    )

    if kits.empty:
        return None

    tamaños = []

    for tamaño in kits["Size"].dropna():
        try:
            tamaños.append(_convertir_x(tamaño))
        except (TypeError, ValueError):
            continue

    return max(tamaños) if tamaños else None


def calcular_x_breakers(catalogo, capacidad, carrito):

    total = 0.0

    if carrito is None or carrito.empty:
        return total

    for _, producto in carrito.iterrows():
        tamaño = obtener_x_para_breaker(
            catalogo,
            capacidad,
            producto
        )

        if tamaño is not None:
            total += tamaño

    return total


def calcular_x_tapas(carrito):

    total = 0.0

    if carrito is None or carrito.empty:
        return total

    for _, producto in carrito.iterrows():
        try:
            total += _convertir_x(producto["Size"])
        except (KeyError, TypeError, ValueError):
            continue

    return total


def calcular_x_principal(catalogo, capacidad, principal):

    if principal is None or principal.empty:
        return 0.0

    tamaño = obtener_x_para_breaker(
        catalogo,
        capacidad,
        principal.iloc[0]
    )

    return tamaño or 0.0


def calcular_espacio_disponible(
    catalogo,
    capacidad,
    altura,
    breakers,
    tapas,
    principal
):

    espacio_total = obtener_espacio_total(
        catalogo,
        capacidad,
        altura
    )

    espacio_usado = (
        calcular_x_breakers(catalogo, capacidad, breakers)
        + calcular_x_tapas(tapas)
        + calcular_x_principal(catalogo, capacidad, principal)
    )

    return max(0.0, espacio_total - espacio_usado)

class EspacioService:

    @staticmethod
    def calcular_x_usadas(
        carrito,
        conectores,
        tapas
    ):

        total = 0

        catalogos = conectores + tapas

        for item in carrito:

            producto = catalogos[
                catalogos["Catalogo"]
                ==
                item["Catalogo"]
            ]

            if producto.empty:
                continue

            size = producto.iloc[0]["Size"]

            ubicacion = producto.iloc[0]["Ubicacion"]

            multiplicador = (
                2
                if str(ubicacion).upper() == "DOBLE"
                else 1
            )

            if pd.notna(size):

                total += (
                    float(
                        str(size)
                        .replace("X", "")
                    )
                    *
                    multiplicador
                    *
                    item["Cantidad"]
                )

        return total