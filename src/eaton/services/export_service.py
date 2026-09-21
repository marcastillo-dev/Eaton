import pandas as pd
from io import BytesIO
from pathlib import Path


COLUMNAS = [
    "Partida",
    "Catalogo",
    "Descripcion",
    "Unidades",
    "Precio Unitario",
    "Subtotal"
]


def _numero(valor, predeterminado=0):

    try:
        return float(valor)
    except (TypeError, ValueError):
        return predeterminado


def _filas_dataframe(dataframe, multiplicador=1.0):

    if dataframe is None or dataframe.empty:
        return []

    filas = []

    for _, item in dataframe.iterrows():
        cantidad = _numero(
            item.get("Cantidad", 1),
            1
        )

        if cantidad <= 0:
            continue

        precio = (
            _numero(item.get("Precio"))
            * multiplicador
        )

        filas.append({
            "Catalogo": item.get("Catalogo", ""),
            "Descripcion": item.get("Descripcion", ""),
            "Unidades": cantidad,
            "Precio Unitario": precio,
            "Subtotal": precio * cantidad
        })

    return filas


def _filas_conectores(orden, catalogo, multiplicador, selecciones):

    breakers = orden.get("breakers", pd.DataFrame())

    if breakers is None or breakers.empty:
        return []

    capacidad = orden.get("capacidad")
    capacidad_conectores = capacidad

    if capacidad == "600 AMP":
        capacidad_conectores = "1600 AMP"
    elif capacidad in ["800 AMP", "1200 AMP"]:
        capacidad_conectores = "2000 AMP"

    filas = []
    agrupacion = [
        "Catalogo",
        "Marco",
        "Corriente",
        "# Polos",
        "Clasificacion"
    ]

    columnas = [col for col in agrupacion if col in breakers.columns]

    for _, breaker in breakers.groupby(
        columnas,
        dropna=False,
        as_index=False
    ).size().iterrows():

        catalogo_breaker = breaker["Catalogo"]
        opciones = catalogo.obtener_kits_conectores_para_breaker(
            capacidad_conectores,
            breaker["Marco"],
            int(breaker["# Polos"]),
            int(_numero(breaker["Corriente"])),
            breaker.get("Clasificacion")
        )

        if opciones.empty:
            continue

        ubicacion = selecciones.get(
            str(catalogo_breaker),
            opciones.iloc[0].get("Ubicacion")
        )

        kit = opciones[
            opciones["Ubicacion"] == ubicacion
        ].copy()

        if kit.empty:
            kit = opciones.iloc[[0]].copy()

        cantidad_breakers = int(breaker["size"])
        cantidad_kits = (
            (cantidad_breakers + 1) // 2
            if ubicacion == "Doble"
            else cantidad_breakers
        )

        for _, item in kit.iterrows():
            precio = _numero(item.get("Precio")) * multiplicador
            filas.append({
                "Catalogo": item.get("Catalogo", ""),
                "Descripcion": item.get("Descripcion", ""),
                "Unidades": cantidad_kits,
                "Precio Unitario": precio,
                "Subtotal": precio * cantidad_kits
            })

    return filas


def _agregar_seccion(worksheet, filas, nombre, fila, formatos):

    if not filas:
        return fila

    worksheet.write(fila, 0, nombre, formatos["section"])
    fila += 1

    for columna, encabezado in enumerate(COLUMNAS):
        worksheet.write(fila, columna, encabezado, formatos["header"])

    fila += 1

    for partida, item in enumerate(filas, start=1):
        valores = [
            partida,
            item["Catalogo"],
            item["Descripcion"],
            item["Unidades"],
            item["Precio Unitario"],
            item["Subtotal"]
        ]

        for columna, valor in enumerate(valores):
            formato = (
                formatos["currency"]
                if columna in [4, 5]
                else formatos["body"]
            )
            worksheet.write(fila, columna, valor, formato)

        fila += 1

    return fila + 1


def _agrupar_filas(filas):

    if not filas:
        return []

    resumen = {}

    for item in filas:
        clave = (
            item.get("Catalogo", ""),
            item.get("Descripcion", "")
        )
        unidades = _numero(item.get("Unidades"))
        subtotal = _numero(item.get("Subtotal"))
        acumulado = resumen.setdefault(
            clave,
            {"Unidades": 0.0, "Subtotal": 0.0}
        )
        acumulado["Unidades"] += unidades
        acumulado["Subtotal"] += subtotal

    filas_resumen = []

    for (catalogo, descripcion), valores in resumen.items():
        unidades = valores["Unidades"]
        subtotal = valores["Subtotal"]
        filas_resumen.append({
            "Catalogo": catalogo,
            "Descripcion": descripcion,
            "Unidades": unidades,
            "Precio Unitario": (
                subtotal / unidades
                if unidades
                else 0
            ),
            "Subtotal": subtotal
        })

    return filas_resumen


def generar_excel_ordenes(ordenes, catalogo, logo):

    output = BytesIO()
    logo = Path(logo)

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        workbook = writer.book
        formatos = {
            "title": workbook.add_format({
                "bold": True,
                "font_size": 18,
                "font_color": "#0A2342",
                "bottom": 2,
                "bottom_color": "#005EB8"
            }),
            "section": workbook.add_format({
                "bold": True,
                "font_size": 12,
                "font_color": "#FFFFFF",
                "bg_color": "#005EB8",
                "align": "left"
            }),
            "header": workbook.add_format({
                "bold": True,
                "font_color": "#FFFFFF",
                "bg_color": "#0A2342",
                "border": 1,
                "align": "center",
                "valign": "vcenter",
                "text_wrap": True
            }),
            "body": workbook.add_format({
                "border": 1,
                "border_color": "#D9E2EC",
                "valign": "top"
            }),
            "currency": workbook.add_format({
                "border": 1,
                "border_color": "#D9E2EC",
                "num_format": '$#,##0.00',
                "align": "right"
            }),
            "total_label": workbook.add_format({
                "bold": True,
                "font_color": "#0A2342",
                "top": 2,
                "top_color": "#005EB8"
            }),
            "total": workbook.add_format({
                "bold": True,
                "font_color": "#0A2342",
                "top": 2,
                "top_color": "#005EB8",
                "num_format": '$#,##0.00'
            })
        }

        filas_resumen = []

        for indice, orden in enumerate(ordenes, start=1):
            numero_orden = orden.get("_numero_orden", indice)
            nombre_hoja = f"Partida #{numero_orden}"
            worksheet = workbook.add_worksheet(nombre_hoja)
            writer.sheets[nombre_hoja] = worksheet
            worksheet.hide_gridlines(2)
            worksheet.set_column("A:A", 10)
            worksheet.set_column("B:B", 22)
            worksheet.set_column("C:C", 52)
            worksheet.set_column("D:D", 16)
            worksheet.set_column("E:F", 18)
            worksheet.set_row(0, 40)

            if logo.is_file():
                worksheet.insert_image(
                    "A1",
                    str(logo),
                    {
                        "x_scale": 0.075,
                        "y_scale": 0.075,
                        "x_offset": 8,
                        "y_offset": 2
                    }
                )

            worksheet.merge_range(
                "C2:F2",
                nombre_hoja,
                formatos["title"]
            )

            multiplicador_tablero = _numero(
                orden.get("multiplicador_tablero", 1.0),
                1.0
            )
            multiplicador_breakers = _numero(
                orden.get("multiplicador_breakers", 1.0),
                1.0
            )
            selecciones = orden.get("selecciones_conectores", {})

            secciones = [
                (
                    "Tablero",
                    _filas_dataframe(
                        orden.get("tablero"),
                        multiplicador_tablero
                    )
                ),
                (
                    "Interruptor Principal",
                    _filas_dataframe(
                        orden.get("interruptor_principal"),
                        multiplicador_breakers
                    )
                ),
                (
                    "Derivados",
                    _filas_dataframe(
                        orden.get("interruptores"),
                        multiplicador_breakers
                    ) + _filas_dataframe(
                        orden.get("breakers"),
                        multiplicador_breakers
                    )
                ),
                (
                    "Kits de Conectores",
                    _filas_conectores(
                        orden,
                        catalogo,
                        multiplicador_tablero,
                        selecciones
                    )
                ),
                (
                    "Tapas",
                    _filas_dataframe(
                        orden.get("tapas"),
                        multiplicador_tablero
                    )
                )
            ]

            fila = 3
            total_calculado = 0

            for nombre, filas in secciones:
                filas_resumen.extend(filas)
                fila = _agregar_seccion(
                    worksheet,
                    filas,
                    nombre,
                    fila,
                    formatos
                )
                total_calculado += sum(
                    item["Subtotal"] for item in filas
                )

            fila += 1
            worksheet.write(fila, 4, "Total", formatos["total_label"])
            worksheet.write(fila, 5, total_calculado, formatos["total"])

        nombre_hoja = "Resumen"
        worksheet = workbook.add_worksheet(nombre_hoja)
        writer.sheets[nombre_hoja] = worksheet
        worksheet.hide_gridlines(2)
        worksheet.set_column("A:A", 10)
        worksheet.set_column("B:B", 22)
        worksheet.set_column("C:C", 52)
        worksheet.set_column("D:D", 16)
        worksheet.set_column("E:F", 18)
        worksheet.set_row(0, 40)

        if logo.is_file():
            worksheet.insert_image(
                "A1",
                str(logo),
                {
                    "x_scale": 0.075,
                    "y_scale": 0.075,
                    "x_offset": 8,
                    "y_offset": 2
                }
            )

        worksheet.merge_range(
            "C2:F2",
            nombre_hoja,
            formatos["title"]
        )

        filas_agrupadas = _agrupar_filas(filas_resumen)
        fila = _agregar_seccion(
            worksheet,
            filas_agrupadas,
            "Componentes",
            3,
            formatos
        )
        total_resumen = sum(
            item["Subtotal"] for item in filas_agrupadas
        )
        fila += 1
        worksheet.write(fila, 4, "Total", formatos["total_label"])
        worksheet.write(fila, 5, total_resumen, formatos["total"])

    return output.getvalue()


def generar_excel(carrito, descuento_factor):
    """Compatibilidad con el exportador antiguo de una sola tabla."""

    datos = []

    for item in carrito:
        precio = _numero(item.get("Precio")) * descuento_factor
        cantidad = _numero(item.get("Cantidad"), 1)
        datos.append({
            "Catalogo": item.get("Catalogo", ""),
            "Descripcion": item.get("Descripcion", ""),
            "Cantidad": cantidad,
            "Precio Lista": _numero(item.get("Precio")),
            "Precio Cliente": round(precio, 2),
            "Subtotal": round(precio * cantidad, 2)
        })

    df_export = pd.DataFrame(datos)
    output = BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_export.to_excel(
            writer,
            index=False,
            sheet_name="Partida"
        )

    return output.getvalue()

