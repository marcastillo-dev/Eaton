# ui/product_card.py

import streamlit as st
import pandas as pd
from src.eaton.services.catalogo_service import CatalogoService
from src.eaton.config.settings import CATALOGO

catalogo = CatalogoService(
    CATALOGO
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
                    color:white;">
                    {catalogo_producto}
                </p>

                <p style="
                    margin-top:0;
                    font-size:12px;
                    color:#C9D1D9;">
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

                        st.session_state.interruptor_principal = (
                            producto.to_frame().T
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
                                    size_tapa = int(
                                        str(producto["Size"])
                                        .replace("X", "")
                                    )
                                except (TypeError, ValueError):
                                    st.error(
                                        "El tamaño de la tapa no es válido."
                                    )
                                    continue

                                espacio_requerido = (
                                    size_tapa * cantidad
                                )

                                if (
                                    espacio_requerido >
                                    st.session_state.espacio_disponible
                                ):

                                    st.toast(
                                        f"⚠️ Necesitas {espacio_requerido}X y sólo quedan "
                                        f"{st.session_state.espacio_disponible}X"
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

                                kit = (
                                    catalogo.obtener_kits_conectores_para_breaker(
                                        "1600 AMP"
                                        if st.session_state.capacidad == "600 AMP"
                                        else (
                                            "2000 AMP"
                                            if st.session_state.capacidad in [
                                                "800 AMP",
                                                "1200 AMP"
                                            ]
                                            else st.session_state.capacidad
                                        ),
                                        producto["Marco"],
                                        int(producto["# Polos"]),
                                        int(producto["Corriente"])
                                    )
                                )

                                if not kit.empty:

                                    try:
                                        x_por_breaker = int(
                                            str(
                                                kit.iloc[0]["Size"]
                                            ).replace("X", "")
                                        )
                                    except (TypeError, ValueError):
                                        st.error(
                                            "El tamaño del kit de conectores no es válido."
                                        )
                                        continue

                                    espacio_requerido = (
                                        x_por_breaker
                                        * cantidad
                                    )

                                    if (
                                        espacio_requerido
                                        >
                                        st.session_state.espacio_disponible
                                    ):

                                        st.toast(
                                            f"⚠️ Necesitas {espacio_requerido}X y sólo quedan "
                                            f"{st.session_state.espacio_disponible}X"
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