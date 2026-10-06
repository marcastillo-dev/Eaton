import pandas as pd
from io import BytesIO
from pathlib import Path


COLUMNAS = [
    "Partida",
    "Catalogo",
    "Descripcion",
    "Unidades",
    "Precio Unitario",
    "Subtotal",
    "Costo",
    "Margen"
]

NOTA_IZMX = (
    "* Para los interruptores de Potencia este precio es estimativo, "
    "el precio correcto lo otorga tu representante de ventas y debe contener "
    "en el catálogo los 16 dígitos que conforman el catálogo completo."
)


def _numero(valor, predeterminado=0):
    try:
        return float(valor)
    except (TypeError, ValueError):
        return predeterminado


def _obtener_costo_y_margen(item, precio_unitario):
    if "Costo" in item and pd.notna(item["Costo"]):
        costo_val = _numero(item["Costo"], None)
        if costo_val is not None and costo_val >= 0:
            if precio_unitario > 0:
                margen_val = (precio_unitario - costo_val) / precio_unitario
            else:
                margen_val = 0.0
            return costo_val, margen_val

    return "N/D", "N/D"


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

        costo, margen = _obtener_costo_y_margen(item, precio)

        filas.append({
            "Catalogo": item.get("Catalogo", ""),
            "Descripcion": item.get("Descripcion", ""),
            "Unidades": cantidad,
            "Precio Unitario": precio,
            "Subtotal": precio * cantidad,
            "Costo": costo,
            "Margen": margen
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
            costo, margen = _obtener_costo_y_margen(item, precio)
            filas.append({
                "Catalogo": item.get("Catalogo", ""),
                "Descripcion": item.get("Descripcion", ""),
                "Unidades": cantidad_kits,
                "Precio Unitario": precio,
                "Subtotal": precio * cantidad_kits,
                "Costo": costo,
                "Margen": margen
            })

    return filas


def _agregar_seccion(worksheet, filas, nombre, fila, formatos, catalogos_izmx=None):

    if not filas:
        return fila

    worksheet.write(fila, 0, nombre, formatos["section"])
    fila += 1

    for columna, encabezado in enumerate(COLUMNAS):
        worksheet.write(fila, columna, encabezado, formatos["header"])

    fila += 1

    tiene_izmx = False

    for partida, item in enumerate(filas, start=1):
        cat_actual = str(item.get("Catalogo", "")).strip()
        if catalogos_izmx and cat_actual in catalogos_izmx:
            tiene_izmx = True

        valores = [
            partida,
            item["Catalogo"],
            item["Descripcion"],
            item["Unidades"],
            item["Precio Unitario"],
            item["Subtotal"],
            item.get("Costo", "N/D"),
            item.get("Margen", "N/D")
        ]

        for columna, valor in enumerate(valores):
            if columna in [4, 5]:
                formato = formatos["currency"]
            elif columna == 6:
                formato = formatos["currency"] if isinstance(valor, (int, float)) else formatos["nd"]
            elif columna == 7:
                formato = formatos["percentage"] if isinstance(valor, (int, float)) else formatos["nd"]
            else:
                formato = formatos["body"]

            worksheet.write(fila, columna, valor, formato)

        fila += 1

    # Si la sección contiene algún interruptor IZMX, se añade la nota debajo
    if tiene_izmx:
        worksheet.set_row(fila, 26)  # Altura suficiente para dos líneas
        worksheet.merge_range(
            fila, 1, fila, len(COLUMNAS) - 1,
            NOTA_IZMX,
            formatos["nota_izmx"]
        )
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
        costo = item.get("Costo")

        acumulado = resumen.setdefault(
            clave,
            {
                "Unidades": 0.0,
                "Subtotal": 0.0,
                "Costo_Suma": 0.0,
                "Tiene_Costo": True if isinstance(costo, (int, float)) else False
            }
        )
        acumulado["Unidades"] += unidades
        acumulado["Subtotal"] += subtotal
        if isinstance(costo, (int, float)):
            acumulado["Costo_Suma"] += (costo * unidades)
        else:
            acumulado["Tiene_Costo"] = False

    filas_resumen = []

    for (catalogo, descripcion), valores in resumen.items():
        unidades = valores["Unidades"]
        subtotal = valores["Subtotal"]
        precio_unitario = subtotal / unidades if unidades else 0

        if valores["Tiene_Costo"] and unidades > 0:
            costo_unitario = valores["Costo_Suma"] / unidades
            margen = (precio_unitario - costo_unitario) / precio_unitario if precio_unitario > 0 else 0.0
        else:
            costo_unitario = "N/D"
            margen = "N/D"

        filas_resumen.append({
            "Catalogo": catalogo,
            "Descripcion": descripcion,
            "Unidades": unidades,
            "Precio Unitario": precio_unitario,
            "Subtotal": subtotal,
            "Costo": costo_unitario,
            "Margen": margen
        })

    return filas_resumen


def generar_excel_ordenes(ordenes, catalogo, logo):

    output = BytesIO()
    logo = Path(logo)

    # Conjunto de catálogos de interruptores IZMX para detección rápida
    try:
        df_hoja_izmx = catalogo.obtener_hoja("Interruptores IZMX")
        catalogos_izmx = set(df_hoja_izmx["Catalogo"].dropna().astype(str).str.strip())
    except Exception:
        catalogos_izmx = set()

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
            "percentage": workbook.add_format({
                "border": 1,
                "border_color": "#D9E2EC",
                "num_format": '0.0%',
                "align": "right"
            }),
            "nd": workbook.add_format({
                "border": 1,
                "border_color": "#D9E2EC",
                "align": "center",
                "font_color": "#627D98"
            }),
            "nota_izmx": workbook.add_format({
                "font_size": 9,
                "italic": True,
                "font_color": "#005EB8",
                "align": "left",
                "valign": "vcenter",
                "text_wrap": True
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
            worksheet.set_column("D:D", 14)
            worksheet.set_column("E:F", 18)
            worksheet.set_column("G:G", 16)
            worksheet.set_column("H:H", 14)
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
                "C2:H2",
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
                    formatos,
                    catalogos_izmx=catalogos_izmx
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
        worksheet.set_column("D:D", 14)
        worksheet.set_column("E:F", 18)
        worksheet.set_column("G:G", 16)
        worksheet.set_column("H:H", 14)
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
            "C2:H2",
            nombre_hoja,
            formatos["title"]
        )

        filas_agrupadas = _agrupar_filas(filas_resumen)
        fila = _agregar_seccion(
            worksheet,
            filas_agrupadas,
            "Componentes",
            3,
            formatos,
            catalogos_izmx=catalogos_izmx
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
        costo, margen = _obtener_costo_y_margen(item, precio)
        datos.append({
            "Catalogo": item.get("Catalogo", ""),
            "Descripcion": item.get("Descripcion", ""),
            "Cantidad": cantidad,
            "Precio Lista": _numero(item.get("Precio")),
            "Precio Cliente": round(precio, 2),
            "Subtotal": round(precio * cantidad, 2),
            "Costo": costo,
            "Margen": margen
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