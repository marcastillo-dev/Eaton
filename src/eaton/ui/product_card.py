# ui/product_card.py

import streamlit as st
import pandas as pd
from src.eaton.services.catalogo_service import CatalogoService
from src.eaton.config.settings import CATALOGO
from src.eaton.services.espacio_service import (
    calcular_espacio_disponible,
    calcular_x_breaker,
    _convertir_x
)

catalogo = CatalogoService(
    CATALOGO
)


def _obtener_espacio_disponible(principal=None):

    capacidad = st.session_state.get("capacidad")
    altura = st.session_state.get("altura")
    acometida = st.session_state.get("acometida")

    if not capacidad:
        return 0.0

    espacio_total_override = (
        50
        if (
            capacidad in ["2000 AMP", "3200 AMP"]
            and acometida in [
                "Chasis de Derivados",
                "Secciones Vacías"
            ]
        )
        else None
    )

    return calcular_espacio_disponible(
        catalogo,
        capacidad,
        altura,
        st.session_state.get("carrito_breakers"),
        st.session_state.get("carrito_tapas"),
        (
            st.session_state.get("interruptor_principal")
            if principal is None
            else principal
        ),
        espacio_total_override,
        st.session_state.get("selecciones_conectores", {})
    )

def mostrar_productos(
    df_productos,
    prefijo,
    mostrar_boton=True,
    marco=None
):

    if prefijo in [
        "breakers",
        "tapas",
        "principal"
    ]:

        busqueda = st.session_state.get(
            "busqueda_productos",
            ""
        ).strip()

        if busqueda:

            texto_productos = (
                df_productos["Catalogo"].fillna("").astype(str)
                + " "
                + df_productos["Descripcion"].fillna("").astype(str)
            )

            df_productos = df_productos[
                texto_productos.str.contains(
                    busqueda,
                    case=False,
                    regex=False,
                    na=False
                )
            ]

    for _, producto in df_productos.iterrows():

        with st.container(border=True):

            if prefijo == "orden":

                c1, c2 = st.columns([8,3])

            elif prefijo in [
                "breakers",
                "tapas",
                "principal"
            ]:

                c1, c2, c3 = st.columns([8,2,2])

            elif prefijo in [
                "breakers_orden",
                "tapas_orden"
            ]:

                c1, c2, c3 = st.columns([6,4,4])


            catalogo_producto = producto["Catalogo"]

            if (
                "Cantidad" in producto.index
                and producto["Cantidad"] > 1
            ):

                catalogo_producto = (
                    f"{catalogo_producto} "
                    f"<span style='color:#22C55E;'>"
                    f"x{int(producto['Cantidad'])}"
                    f"</span>"
                )

            c1.markdown(
                f"""
                <p style="
                    margin-bottom:0;
                    font-size:18px;
                    font-weight:bold;
                    color:var(--text-primary);">
                    {catalogo_producto}
                </p>

                <p style="
                    margin-top:0;
                    font-size:12px;
                    color:var(--text-secondary);">
                    {producto['Descripcion']}
                </p>
                """,
                unsafe_allow_html=True
            )

            c2.markdown(
                f"""
                <div style="
                    text-align:center;
                    padding-top:18px;
                    font-size:18px;">
                    ${producto['Precio']:,.0f}
                </div>
                """,
                unsafe_allow_html=True
            )   

            if (
                mostrar_boton
                and prefijo in [
                    "breakers",
                    "tapas",
                    "principal"
                ]
            ):

                c3.markdown(
                    "<div style='margin-top:10px'></div>",
                    unsafe_allow_html=True
                )

                if prefijo == "principal":

                    if c3.button(
                        "Seleccionar",
                        key=f"seleccionar_{producto['Catalogo']}",
                        use_container_width=True
                    ):

                        nuevo_principal = producto.to_frame().T
                        espacio_disponible = (
                            _obtener_espacio_disponible(
                                pd.DataFrame()
                            )
                        )

                        x_principal = calcular_x_breaker(
                            catalogo,
                            st.session_state.capacidad,
                            producto,
                            1
                        )

                        if (
                            x_principal is None
                            or x_principal > espacio_disponible
                        ):
                            st.toast(
                                f"⚠️ No hay espacio suficiente para este interruptor. "
                                f"Necesitas {x_principal or 0}X y sólo quedan "
                                f"{espacio_disponible}X"
                            )
                        else:
                            st.session_state.interruptor_principal = (
                                nuevo_principal
                            )

                            st.rerun()

                else:

                    with c3.popover(
                        "Agregar",
                        use_container_width=True
                    ):

                        cantidad = st.number_input(
                            "Cantidad",
                            min_value=1,
                            value=1,
                            step=1,
                            key=f"cant_{prefijo}_{producto['Catalogo']}"
                        )

                        if st.button(
                            "Confirmar",
                            key=f"confirmar_{prefijo}_{producto['Catalogo']}"
                        ):

                            if prefijo == "principal":

                                st.session_state.interruptor_principal = (
                                    producto.to_frame().T
                                )

                                st.rerun()

                            if prefijo == "tapas":

                                try:
                                    size_tapa = _convertir_x(
                                        producto["Size"]
                                    )
                                except (TypeError, ValueError):
                                    st.error(
                                        "El tamaño de la tapa no es válido."
                                    )
                                    continue

                                espacio_disponible = (
                                    _obtener_espacio_disponible()
                                )

                                espacio_requerido = size_tapa * cantidad

                                if (
                                    espacio_requerido >
                                    espacio_disponible
                                ):

                                    st.toast(
                                        f"⚠️ Necesitas {espacio_requerido}X y sólo quedan "
                                        f"{espacio_disponible}X"
                                    )

                                else:

                                    producto = producto.copy()

                                    nuevo = pd.DataFrame(
                                        [producto] * cantidad
                                    )

                                    st.session_state.carrito_tapas = pd.concat(
                                        [
                                            st.session_state.carrito_tapas,
                                            nuevo
                                        ],
                                        ignore_index=True
                                    )

                                    st.rerun()

                            producto = producto.copy()

                            nuevo = pd.DataFrame(
                                [producto] * cantidad
                            )

                            if prefijo == "breakers":

                                x_por_breaker = calcular_x_breaker(
                                    catalogo,
                                    st.session_state.capacidad,
                                    producto,
                                    cantidad
                                )

                                if x_por_breaker is not None:

                                    try:
                                        espacio_disponible = (
                                            _obtener_espacio_disponible()
                                        )
                                    except (TypeError, ValueError, KeyError):
                                        st.error(
                                            "No se pudo calcular el espacio disponible."
                                        )
                                        continue

                                    espacio_requerido = x_por_breaker

                                    if (
                                        espacio_requerido
                                        >
                                        espacio_disponible
                                    ):

                                        st.toast(
                                            f"⚠️ Necesitas {espacio_requerido}X y sólo quedan "
                                            f"{espacio_disponible}X"
                                        )

                                    else:

                                        st.session_state.carrito_breakers = pd.concat(
                                            [
                                                st.session_state.carrito_breakers,
                                                nuevo
                                            ],
                                            ignore_index=True
                                        )

                                        st.rerun()

                                else:
                                    st.warning(
                                        "No existe un kit de conectores para este breaker."
                                    )

            if prefijo in [
                "breakers_orden",
                "tapas_orden"
            ]:

                c3.markdown(
                    "<div style='margin-top:10px'></div>",
                    unsafe_allow_html=True
                )

                with c3.popover(
                    "Quitar",
                    use_container_width=True
                ):

                    cantidad_quitar = st.number_input(
                        "Cantidad",
                        min_value=1,
                        max_value=int(producto["Cantidad"]),
                        value=1,
                        step=1,
                        key=f"quitar_cant_{prefijo}_{producto['Catalogo']}"
                    )

                    if st.button(
                        "Confirmar",
                        key=f"confirmar_quitar_{prefijo}_{producto['Catalogo']}"
                    ):

                        carrito = (
                            st.session_state.carrito_breakers
                            if prefijo == "breakers_orden"
                            else st.session_state.carrito_tapas
                        )

                        filas_producto = (
                            carrito[
                                carrito["Catalogo"]
                                == producto["Catalogo"]
                            ]
                        )

                        indices = (
                            filas_producto.index[:cantidad_quitar]
                        )

                        if prefijo == "breakers_orden":

                            st.session_state.carrito_breakers = (
                                st.session_state.carrito_breakers
                                .drop(indices)
                                .reset_index(drop=True)
                            )

                        else:

                            st.session_state.carrito_tapas = (
                                st.session_state.carrito_tapas
                                .drop(indices)
                                .reset_index(drop=True)
                            )

                        st.session_state.toast_breaker = (
                            f"✅ Se eliminaron "
                            f"{cantidad_quitar} piezas"
                        )

                        st.rerun()