import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

def generar_excel(carrito, descuento_factor):

    datos = []

    for item in carrito:

        precio_desc = item["Precio"] * descuento_factor

        datos.append({
            "Catalogo": item["Catalogo"],
            "Descripcion": item["Descripcion"],
            "Cantidad": item["Cantidad"],
            "Precio Lista": item["Precio"],
            "Precio Cliente": round(precio_desc, 2),
            "Subtotal": round(
                precio_desc * item["Cantidad"],
                2
            )
        })

    df_export = pd.DataFrame(datos)

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="xlsxwriter"
    ) as writer:

        df_export.to_excel(
            writer,
            index=False,
            sheet_name="Orden"
        )

    return output.getvalue()

