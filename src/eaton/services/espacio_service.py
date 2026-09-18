# services/espacio_service.py

import pandas as pd

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