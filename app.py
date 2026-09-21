import pandas as pd
import streamlit as st
from src.eaton.services.catalogo_service import CatalogoService
from src.eaton.services.espacio_service import (
    calcular_espacio_disponible,
    obtener_espacio_total
)
from src.eaton.config.settings import ASSETS_DIR, CATALOGO, LOGO
from src.eaton.ui.styles import cargar_estilos
from src.eaton.ui.header import render_header
from src.eaton.ui.product_card import (
    mostrar_productos
)

st.set_page_config(
    page_title="EDS Orders",
    page_icon=str(LOGO),
    layout="wide"
)

cargar_estilos()

render_header()

if "toast_breaker" in st.session_state:

    st.toast(
        st.session_state.toast_breaker
    )

    del st.session_state.toast_breaker

catalogo = CatalogoService(
    CATALOGO
)

imagenes_marco = {
    marco: str(ASSETS_DIR / f"{marco}.png")
    for marco in ["BZM", "PDG", "F", "J", "K", "L"]
}

if "ordenes_guardadas" not in st.session_state:

    st.session_state.ordenes_guardadas = []

if "carrito_breakers" not in st.session_state:

    st.session_state.carrito_breakers = pd.DataFrame()

if "carrito_tapas" not in st.session_state:

    st.session_state.carrito_tapas = pd.DataFrame()

if "espacio_disponible" not in st.session_state:

    st.session_state.espacio_disponible = 999

if "orden_editando" not in st.session_state:

    st.session_state.orden_editando = None

if "interruptor_principal" not in st.session_state:

    st.session_state.interruptor_principal = pd.DataFrame()

if st.session_state.get("limpiar_todo", False):

    ordenes_guardadas = (
        st.session_state.get(
            "ordenes_guardadas",
            []
        )
    )

    st.session_state.clear()

    st.session_state["ordenes_guardadas"] = (
        ordenes_guardadas
    )

    st.rerun()

col1, espacio, col2 = st.columns([2,0.25,1])

with col1:

    busqueda = st.text_input(
        "Buscar producto",
        key="busqueda_productos"
    )

    capacidades = sorted(
        catalogo.obtener_estructura()["Capacidad"]
        .dropna()
        .unique()
    )

    indice_capacidad = None

    if st.session_state.orden_editando:

        capacidad_guardada = (
            st.session_state.orden_editando.get(
                "capacidad"
            )
        )

        if capacidad_guardada in capacidades:

            indice_capacidad = capacidades.index(
                capacidad_guardada
            )

    capacidad = st.selectbox(
        "Capacidad",
        capacidades,
        index=indice_capacidad,
        key="capacidad",
        placeholder="Selecciona una capacidad"
    )

    configuracion = None
    acometida = None
    montaje = None
    altura = None
    entrada_cables = None

    kits_seleccionados = pd.DataFrame()

    incluir_medicion = False
    incluir_bus = False
    incluir_sensor = False

    marco = None
    tipo = None
    operacion = None
    lsig = False
    usar_breakers = "No"

    puerta = pd.DataFrame()
    
    if capacidad:

        if capacidad in [
            "600 AMP",
            "800 AMP",
            "1200 AMP"
        ]:

            alturas = list(
                catalogo.obtener_alturas_por_capacidad(
                    capacidad
                )
            )

            indice_altura = None

            if st.session_state.orden_editando:

                altura_guardada = (
                    st.session_state.orden_editando.get(
                        "altura"
                    )
                )

                if altura_guardada in alturas:

                    indice_altura = (
                        alturas.index(
                            altura_guardada
                        )
                    )

            altura = st.selectbox(
                "Altura",
                alturas,
                index=indice_altura,
                key="altura",
                placeholder="Selecciona una altura"
            )

            if altura:

                estructuras = (
                    catalogo.obtener_estructura_por_capacidad_y_altura(
                        capacidad,
                        altura
                    )
                )

                acometidas = list(
                    catalogo.obtener_acometidas_por_capacidad(
                        capacidad
                    )
                )

                if "Interruptor principal" not in acometidas:

                    acometidas = list(acometidas)

                    acometidas.append(
                        "Interruptor principal"
                    )

                indice_acometida = None

                if st.session_state.orden_editando:

                    acometida_guardada = (
                        st.session_state.orden_editando.get(
                            "acometida"
                        )
                    )

                    if acometida_guardada in acometidas:

                        indice_acometida = (
                            acometidas.index(
                                acometida_guardada
                            )
                        )

                acometida = st.selectbox(
                    "Acometida",
                    acometidas,
                    index=indice_acometida,
                    key="acometida",
                    placeholder="Selecciona una acometida"
                )

                if acometida != "Interruptor principal":

                    st.session_state.interruptor_principal = pd.DataFrame()

                if (
                    capacidad == "600 AMP"
                    and acometida in [
                        "Interruptor principal",
                        "Zapatas principales"
                    ]
                ):

                    # st.divider()

                    st.session_state.espacio_disponible = (
                        catalogo.obtener_espacio_por_capacidad_y_altura(
                            capacidad,
                            altura
                        )
                    )

                    if acometida == "Zapatas principales":

                        st.divider()

                        st.subheader(
                            "Interruptores Derivados"
                        )

                        marco_derivado = st.selectbox(
                            "Marco",
                            catalogo.obtener_marcos(),
                            index=None,
                            key="marco_derivado_600"
                        )

                        if marco_derivado:

                            if marco_derivado in imagenes_marco:

                                st.image(
                                    imagenes_marco[marco_derivado],
                                    width="stretch"
                                )

                            tipos = (
                                catalogo.obtener_tipos_por_marco(
                                    "1600 AMP",
                                    marco_derivado
                                )
                            )

                            tipo_derivado = st.selectbox(
                                "Tipo",
                                tipos,
                                index=None,
                                key="tipo_derivado_600"
                            )

                            if tipo_derivado:

                                breakers = (
                                    catalogo.obtener_breakers(
                                        "1600 AMP",
                                        marco_derivado,
                                        tipo_derivado
                                    )
                                )

                                breakers = breakers[
                                    breakers["Corriente"] <= 400
                                ]

                                breakers = breakers.copy()

                                breakers["Marco"] = marco_derivado

                                mostrar_productos(
                                    breakers,
                                    "breakers",
                                    mostrar_boton=True
                                )

                                tapas = (
                                    catalogo.obtener_tapas_por_capacidad(
                                        "600 AMP"
                                    )
                                )

                                if not tapas.empty:

                                    st.divider()

                                    st.subheader(
                                        "Tapas"
                                    )

                                    mostrar_productos(
                                        tapas,
                                        "tapas",
                                        mostrar_boton=True
                                    )

                    else:

                        if altura == 73:
                            marcos_principal = ["BZM", "PDG", "L"]
                        else:
                            marcos_principal = ["BZM", "PDG", "K"]

                        indice_marco = None

                        if st.session_state.orden_editando:

                            marco_guardado = (
                                st.session_state.orden_editando.get(
                                    "marco_principal",
                                    st.session_state.orden_editando.get(
                                        "marco"
                                    )
                                )
                            )

                            if marco_guardado in marcos_principal:

                                indice_marco = (
                                    marcos_principal.index(
                                        marco_guardado
                                    )
                                )

                        st.divider()

                        marco = st.selectbox(
                            "Marco",
                            marcos_principal,
                            index=indice_marco,
                            key="marco",
                            placeholder="Selecciona un marco"
                        )

                        if marco is None:

                            st.session_state.interruptor_principal = pd.DataFrame()

                        if marco == "BZM":

                            breakers = (
                                catalogo.obtener_hoja("BZM")
                                .copy()
                            )

                            breakers = breakers[
                                (breakers["Size"] == 3)
                                &
                                (breakers["Corriente"] == 400)
                            ]

                            breakers["Marco"] = "BZM"

                            if (
                                acometida == "Interruptor principal"
                                and st.session_state.interruptor_principal.empty
                            ):
                                mostrar_productos(
                                    breakers,
                                    "principal",
                                    mostrar_boton=True
                                )

                            elif (
                                acometida == "Zapatas principales"
                                or not st.session_state.interruptor_principal.empty
                            ):

                                st.divider()

                                st.subheader(
                                    "Interruptores Derivados"
                                )

                                marco_derivado = st.selectbox(
                                    "Marco",
                                    catalogo.obtener_marcos(),
                                    index=None,
                                    key="marco_derivado"
                                )

                                if marco_derivado:

                                    if marco_derivado in imagenes_marco:

                                        st.image(
                                            imagenes_marco[marco_derivado],
                                            width="stretch"
                                        )

                                    tipos = (
                                        catalogo.obtener_tipos_por_marco(
                                            "1600 AMP",
                                            marco_derivado
                                        )
                                    )

                                    tipo_derivado = st.selectbox(
                                        "Tipo",
                                        tipos,
                                        index=None,
                                        key="tipo_derivado"
                                    )

                                    if tipo_derivado:

                                        breakers = breakers[
                                            breakers["Corriente"] <= 400
                                        ]

                                        breakers = breakers.copy()

                                        breakers["Marco"] = marco_derivado

                                        mostrar_productos(
                                            breakers,
                                            "breakers",
                                            mostrar_boton=True
                                        )

                                        tapas = (
                                            catalogo.obtener_tapas_por_capacidad(
                                                "600 AMP"
                                            )
                                        )

                                        if not tapas.empty:

                                            st.divider()

                                            st.subheader(
                                                "Tapas"
                                            )

                                            mostrar_productos(
                                                tapas,
                                                "tapas",
                                                mostrar_boton=True
                                            )

                        elif marco == "PDG":

                            breakers = (
                                catalogo.obtener_hoja("PDG")
                                .copy()
                            )

                            breakers = breakers[
                                (breakers["Tamano"] == 3)
                                &
                                (
                                    breakers["Tipo"]
                                    .isin(
                                        [
                                            "G",
                                            "M"
                                        ]
                                    )
                                )
                            ]

                            breakers["Marco"] = "PDG"

                            if (
                                acometida == "Interruptor principal"
                                and st.session_state.interruptor_principal.empty
                            ):
                                mostrar_productos(
                                    breakers,
                                    "principal",
                                    mostrar_boton=True
                                )

                            elif (
                                acometida == "Zapatas principales"
                                or not st.session_state.interruptor_principal.empty
                            ):

                                st.divider()

                                st.subheader(
                                    "Interruptores Derivados"
                                )

                                marco_derivado = st.selectbox(
                                    "Marco",
                                    catalogo.obtener_marcos(),
                                    index=None,
                                    key="marco_derivado"
                                )

                                if marco_derivado:

                                    if marco_derivado in imagenes_marco:

                                        st.image(
                                            imagenes_marco[marco_derivado],
                                            width="stretch"
                                        )

                                    tipos = (
                                        catalogo.obtener_tipos_por_marco(
                                            "1600 AMP",
                                            marco_derivado
                                        )
                                    )

                                    tipo_derivado = st.selectbox(
                                        "Tipo",
                                        tipos,
                                        index=None,
                                        key="tipo_derivado"
                                    )

                                    if tipo_derivado:

                                        breakers = (
                                            catalogo.obtener_breakers(
                                                "1600 AMP",
                                                marco_derivado,
                                                tipo_derivado
                                            )
                                        )

                                        breakers = breakers[
                                            breakers["Corriente"] <= 400
                                        ]

                                        breakers = breakers.copy()

                                        breakers["Marco"] = marco_derivado

                                        mostrar_productos(
                                            breakers,
                                            "breakers",
                                            mostrar_boton=True
                                        )

                                        tapas = (
                                            catalogo.obtener_tapas_por_capacidad(
                                                "600 AMP"
                                            )
                                        )

                                        if not tapas.empty:

                                            st.divider()

                                            st.subheader(
                                                "Tapas"
                                            )

                                            mostrar_productos(
                                                tapas,
                                                "tapas",
                                                mostrar_boton=True
                                            )

                        elif marco in ["K", "L"]:

                            breakers = (
                                catalogo.obtener_hoja(marco)
                                .copy()
                            )

                            breakers = breakers[
                                (breakers["Corriente"] == 400)
                                &
                                (breakers["Catalogo"] != "KDB3400L")
                            ]

                            breakers["Marco"] = marco

                            if (
                                acometida == "Interruptor principal"
                                and st.session_state.interruptor_principal.empty
                            ):
                                mostrar_productos(
                                    breakers,
                                    "principal",
                                    mostrar_boton=True
                                )

                            elif (
                                acometida == "Zapatas principales"
                                or not st.session_state.interruptor_principal.empty
                            ):

                                st.divider()

                                st.subheader(
                                    "Interruptores Derivados"
                                )

                                marco_derivado = st.selectbox(
                                    "Marco",
                                    catalogo.obtener_marcos(),
                                    index=None,
                                    key="marco_derivado"
                                )

                                if marco_derivado:

                                    if marco_derivado in imagenes_marco:

                                        st.image(
                                            imagenes_marco[marco_derivado],
                                            width="stretch"
                                        )

                                    tipos = (
                                        catalogo.obtener_tipos_por_marco(
                                            "1600 AMP",
                                            marco_derivado
                                        )
                                    )

                                    tipo_derivado = st.selectbox(
                                        "Tipo",
                                        tipos,
                                        index=None,
                                        key="tipo_derivado"
                                    )

                                    if tipo_derivado:

                                        breakers = (
                                            catalogo.obtener_breakers(
                                                "1600 AMP",
                                                marco_derivado,
                                                tipo_derivado
                                            )
                                        )

                                        breakers = (
                                            catalogo.obtener_breakers(
                                                "1600 AMP",
                                                marco_derivado,
                                                tipo_derivado
                                            )
                                        )

                                        breakers = breakers[
                                            breakers["Corriente"] <= 400
                                        ]

                                        breakers = breakers.copy()

                                        breakers["Marco"] = marco_derivado

                                        mostrar_productos(
                                            breakers,
                                            "breakers",
                                            mostrar_boton=True
                                        )

                                        tapas = (
                                            catalogo.obtener_tapas_por_capacidad(
                                                "600 AMP"
                                            )
                                        )

                                        if not tapas.empty:

                                            st.divider()

                                            st.subheader(
                                                "Tapas"
                                            )

                                            mostrar_productos(
                                                tapas,
                                                "tapas",
                                                mostrar_boton=True
                                            )

                elif (
                    capacidad == "800 AMP"
                    and acometida in [
                        "Interruptor principal",
                        "Zapatas principales"
                    ]
                ):

                    st.divider()

                    st.session_state.espacio_disponible = (
                        catalogo.obtener_espacio_por_capacidad_y_altura(
                            capacidad,
                            altura
                        )
                    )

                    if acometida == "Zapatas principales":

                        st.divider()

                        st.subheader(
                            "Interruptores Derivados"
                        )

                        marco_derivado = st.selectbox(
                            "Marco",
                            catalogo.obtener_marcos(),
                            index=None,
                            key="marco_derivado_800"
                        )

                        if marco_derivado:

                            if marco_derivado in imagenes_marco:

                                st.image(
                                    imagenes_marco[marco_derivado],
                                    width="stretch"
                                )

                            tipos = (
                                catalogo.obtener_tipos_por_marco(
                                    "2000 AMP",
                                    marco_derivado
                                )
                            )

                            tipo_derivado = st.selectbox(
                                "Tipo",
                                tipos,
                                index=None,
                                key="tipo_derivado_800"
                            )

                            if tipo_derivado:

                                breakers = (
                                    catalogo.obtener_breakers(
                                        "2000 AMP",
                                        marco_derivado,
                                        tipo_derivado
                                    )
                                )

                                breakers = breakers[
                                    breakers["Corriente"] <= 600
                                ]

                                breakers = breakers.copy()

                                breakers["Marco"] = marco_derivado

                                mostrar_productos(
                                    breakers,
                                    "breakers",
                                    mostrar_boton=True
                                )

                                tapas = (
                                    catalogo.obtener_tapas_por_capacidad(
                                        "800 AMP"
                                    )
                                )

                                if not tapas.empty:

                                    st.divider()

                                    st.subheader(
                                        "Tapas"
                                    )

                                    mostrar_productos(
                                        tapas,
                                        "tapas",
                                        mostrar_boton=True
                                    )

                    else:

                        indice_marco_principal = None

                        if st.session_state.orden_editando:
                            marco_principal_guardado = (
                                st.session_state.orden_editando.get(
                                    "marco_principal",
                                    st.session_state.orden_editando.get(
                                        "marco"
                                    )
                                )
                            )

                            if marco_principal_guardado == "PDG":
                                indice_marco_principal = 0

                        marco = st.selectbox(
                            "Marco",
                            [
                                "PDG"
                            ],
                            index=indice_marco_principal,
                            key="marco",
                            placeholder="Selecciona un marco"
                        )

                        if marco == "PDG":

                            breakers = (
                                catalogo.obtener_hoja("PDG")
                                .copy()
                            )

                            breakers = breakers[
                                (breakers["Tamano"] == 4)
                                &
                                (breakers["Corriente"].isin([600, 800]))
                            ]

                            breakers["Marco"] = "PDG"
                            
                            if (
                                "interruptor_principal" in st.session_state
                                and st.session_state.interruptor_principal.empty
                            ):

                                mostrar_productos(
                                    breakers,
                                    "principal",
                                    mostrar_boton=True
                                )

                            elif not st.session_state.interruptor_principal.empty:

                                st.divider()

                                st.subheader(
                                    "Interruptores Derivados"
                                )

                                marco_derivado = st.selectbox(
                                    "Marco",
                                    catalogo.obtener_marcos(),
                                    index=None,
                                    key="marco_derivado"
                                )

                                if marco_derivado:

                                    if marco_derivado in imagenes_marco:

                                        st.image(
                                            imagenes_marco[marco_derivado],
                                            width="stretch"
                                        )

                                    tipos = (
                                        catalogo.obtener_tipos_por_marco(
                                            "2000 AMP",
                                            marco_derivado
                                        )
                                    )

                                    tipo_derivado = st.selectbox(
                                        "Tipo",
                                        tipos,
                                        index=None,
                                        key="tipo_derivado"
                                    )

                                    if tipo_derivado:

                                        breakers = (
                                            catalogo.obtener_breakers(
                                                "2000 AMP",
                                                marco_derivado,
                                                tipo_derivado
                                            )
                                        )

                                        breakers = breakers[
                                            breakers["Corriente"] <= 600
                                        ]

                                        breakers = breakers.copy()

                                        breakers["Marco"] = marco_derivado

                                        mostrar_productos(
                                            breakers,
                                            "breakers",
                                            mostrar_boton=True
                                        )

                                        tapas = (
                                            catalogo.obtener_tapas_por_capacidad(
                                                "800 AMP"
                                            )
                                        )

                                        if not tapas.empty:

                                            st.divider()

                                            st.subheader(
                                                "Tapas"
                                            )

                                            mostrar_productos(
                                                tapas,
                                                "tapas",
                                                mostrar_boton=True
                                            )

                elif (
                    capacidad == "1200 AMP"
                    and acometida in [
                        "Interruptor principal",
                        "Zapatas principales"
                    ]
                ):

                    st.divider()

                    if acometida == "Zapatas principales":
                    
                        st.divider()

                        st.subheader(
                            "Interruptores Derivados"
                        )

                        marco_derivado = st.selectbox(
                            "Marco",
                            catalogo.obtener_marcos(),
                            index=None,
                            key="marco_derivado_1200"
                        )

                        if marco_derivado:

                            if marco_derivado in imagenes_marco:
                            
                                st.image(
                                    imagenes_marco[marco_derivado],
                                    width="stretch"
                                )

                            tipos = (
                                catalogo.obtener_tipos_por_marco(
                                    "2000 AMP",
                                    marco_derivado
                                )
                            )

                            tipo_derivado = st.selectbox(
                                "Tipo",
                                tipos,
                                index=None,
                                key="tipo_derivado_1200"
                            )

                            if tipo_derivado:

                                breakers = (
                                    catalogo.obtener_breakers(
                                        "2000 AMP",
                                        marco_derivado,
                                        tipo_derivado
                                    )
                                )

                                breakers = breakers[
                                    breakers["Corriente"] <= 800
                                ]

                                breakers = breakers.copy()

                                breakers["Marco"] = marco_derivado

                                mostrar_productos(
                                    breakers,
                                    "breakers",
                                    mostrar_boton=True
                                )

                                tapas = (
                                    catalogo.obtener_tapas_por_capacidad(
                                        "1200 AMP"
                                    )
                                )

                                if not tapas.empty:

                                    st.divider()

                                    st.subheader(
                                        "Tapas"
                                    )

                                    mostrar_productos(
                                        tapas,
                                        "tapas",
                                        mostrar_boton=True
                                    )

                    else:

                        indice_marco_principal = None

                        if st.session_state.orden_editando:
                            marco_principal_guardado = (
                                st.session_state.orden_editando.get(
                                    "marco_principal",
                                    st.session_state.orden_editando.get(
                                        "marco"
                                    )
                                )
                            )

                            if marco_principal_guardado == "PDG":
                                indice_marco_principal = 0

                        marco = st.selectbox(
                            "Marco",
                            [
                                "PDG"
                            ],
                            index=indice_marco_principal,
                            key="marco",
                            placeholder="Selecciona un marco"
                        )

                        if marco == "PDG":

                            breakers = (
                                catalogo.obtener_hoja("PDG")
                                .copy()
                            )

                            breakers = breakers[
                                breakers["Tamano"] == 5 
                            ]

                            breakers["Marco"] = "PDG"
                            
                            if (
                                "interruptor_principal" in st.session_state
                                and st.session_state.interruptor_principal.empty
                            ):

                                mostrar_productos(
                                    breakers,
                                    "principal",
                                    mostrar_boton=True
                                )

                            elif not st.session_state.interruptor_principal.empty:

                                st.divider()

                                st.subheader(
                                    "Interruptores Derivados"
                                )

                                marco_derivado = st.selectbox(
                                    "Marco",
                                    catalogo.obtener_marcos(),
                                    index=None,
                                    key="marco_derivado"
                                )

                                if marco_derivado:

                                    if marco_derivado:

                                        if marco_derivado in imagenes_marco:

                                            st.image(
                                            imagenes_marco[marco_derivado],
                                            width="stretch"
                                            )

                                        tipos = (
                                            catalogo.obtener_tipos_por_marco(
                                                "2000 AMP",
                                                marco_derivado
                                            )
                                        )

                                    tipos = (
                                        catalogo.obtener_tipos_por_marco(
                                            "2000 AMP",
                                            marco_derivado
                                        )
                                    )

                                    tipo_derivado = st.selectbox(
                                        "Tipo",
                                        tipos,
                                        index=None,
                                        key="tipo_derivado"
                                    )

                                    if tipo_derivado:

                                        breakers = (
                                            catalogo.obtener_breakers(
                                                "2000 AMP",
                                                marco_derivado,
                                                tipo_derivado
                                            )
                                        )

                                        breakers = breakers[
                                            breakers["Corriente"] <= 800
                                        ]

                                        breakers = breakers.copy()

                                        breakers["Marco"] = marco_derivado

                                        mostrar_productos(
                                            breakers,
                                            "breakers",
                                            mostrar_boton=True
                                        )

                                        tapas = (
                                            catalogo.obtener_tapas_por_capacidad(
                                                "1200 AMP"
                                            )
                                        )

                                        if not tapas.empty:

                                            st.divider()

                                            st.subheader(
                                                "Tapas"
                                            )

                                            mostrar_productos(
                                                tapas,
                                                "tapas",
                                                mostrar_boton=True
                                            )

        else:

            if capacidad == "1600 AMP":

                configuraciones = list(
                    catalogo.obtener_configuraciones_1600()
                )

                indice_configuracion = None

                if st.session_state.orden_editando:

                    configuracion_guardada = (
                        st.session_state.orden_editando.get(
                            "configuracion"
                        )
                    )

                    if configuracion_guardada in configuraciones:

                        indice_configuracion = (
                            configuraciones.index(
                                configuracion_guardada
                            )
                        )

                configuracion = st.selectbox(
                    "Configuración",
                    configuraciones,
                    index=indice_configuracion,
                    key="configuracion",
                    placeholder="Selecciona una configuración"
                )

                if configuracion == "Alimentador":

                    pass

                elif configuracion == "Chasis":

                    acometidas = list(
                        catalogo.obtener_acometidas_1600(
                            configuracion
                        )
                    )

                    indice_acometida = None

                    if st.session_state.orden_editando:

                        acometida_guardada = (
                            st.session_state.orden_editando.get(
                                "acometida"
                            )
                        )

                        if acometida_guardada in acometidas:

                            indice_acometida = (
                                acometidas.index(
                                    acometida_guardada
                                )
                            )

                    acometida = st.selectbox(
                        "Acometida",
                        acometidas,
                        index=indice_acometida,
                        key="acometida",
                        placeholder="Selecciona una acometida"
                    )

                    if acometida:

                        entradas = [
                            "Superior",
                            "Inferior"
                        ]

                        indice_entrada = None

                        if st.session_state.orden_editando:

                            entrada_guardada = (
                                st.session_state.orden_editando.get(
                                    "entrada_cables"
                                )
                            )

                            if entrada_guardada in entradas:

                                indice_entrada = (
                                    entradas.index(
                                        entrada_guardada
                                    )
                                )

                        entrada_cables = st.selectbox(
                            "Entrada de cables",
                            entradas,
                            index=indice_entrada,
                            key="entrada_cables",
                            placeholder="Selecciona una entrada"
                        )

                        if entrada_cables:

                            puerta = (
                                catalogo.obtener_puerta_por_entrada(
                                    entrada_cables
                                )
                            )

                        if (
                            acometida == "Interruptor principal"
                            and entrada_cables
                        ):

                            montajes = (
                                catalogo.obtener_montajes_1600(
                                    configuracion,
                                    acometida
                                )
                            )

                            indice_montaje = None

                            if st.session_state.orden_editando:

                                montaje_guardado = (
                                    st.session_state.orden_editando.get(
                                        "montaje"
                                    )
                                )

                                if montaje_guardado in montajes:

                                    indice_montaje = (
                                        montajes.index(
                                            montaje_guardado
                                        )
                                    )

                            montaje = st.selectbox(
                                "Montaje",
                                montajes,
                                index=indice_montaje,
                                key="montaje",
                                placeholder="Selecciona un montaje"
                            )

            elif capacidad in [
                "2000 AMP",
                "3200 AMP"
            ]:

                acometidas = list(
                    catalogo.obtener_acometidas_por_capacidad(
                        capacidad
                    )
                )

                acometidas.extend(
                    [
                        "Chasis de Derivados",
                        "Secciones Vacías"
                    ]
                )

                indice_acometida = None

                if st.session_state.orden_editando:

                    acometida_guardada = (
                        st.session_state.orden_editando.get(
                            "acometida"
                        )
                    )

                    if acometida_guardada in acometidas:

                        indice_acometida = (
                            acometidas.index(
                                acometida_guardada
                            )
                        )

                acometida = st.selectbox(
                    "Acometida",
                    acometidas,
                    index=indice_acometida,
                    key="acometida",
                    placeholder="Selecciona una acometida"
                )

                if acometida in [
                    "Chasis de Derivados"
                ]:

                    usar_breakers = st.radio(
                        "Interruptores Derivados",
                        ["No", "Sí"],
                        horizontal=True
                    )

                if acometida:

                    if acometida == "Interruptor principal":

                        montajes = (
                            catalogo.obtener_montajes_por_capacidad(
                                capacidad,
                                acometida
                            )
                        )

                        indice_montaje = None

                        if st.session_state.orden_editando:

                            montaje_guardado = (
                                st.session_state.orden_editando.get(
                                    "montaje"
                                )
                            )

                            if montaje_guardado in montajes:

                                indice_montaje = (
                                    montajes.index(
                                        montaje_guardado
                                    )
                                )

                        montaje = st.selectbox(
                            "Montaje",
                            montajes,
                            index=indice_montaje,
                            key="montaje",
                            placeholder="Selecciona un montaje"
                        )

            mostrar_kits = (
                (
                    capacidad == "1600 AMP"
                    and (
                        (
                            configuracion == "Alimentador"
                            and entrada_cables
                        )
                        or
                        (
                            configuracion == "Chasis"
                            and acometida
                            and entrada_cables
                            and (
                                acometida == "Zapatas principales"
                                or montaje
                            )
                        )
                    )
                )
                or
                (
                    capacidad in [
                        "2000 AMP",
                        "3200 AMP"
                    ]
                    and acometida == "Interruptor principal"
                    and montaje
                )
            )

            if mostrar_kits:

                st.subheader("Kits")

                valor_medicion = False

                if st.session_state.orden_editando:

                    valor_medicion = (
                        st.session_state.orden_editando.get(
                            "incluir_medicion",
                            False
                        )
                    )

                incluir_medicion = st.checkbox(
                    "Medición",
                    value=valor_medicion
                )

                valor_bus = False

                if st.session_state.orden_editando:

                    valor_bus = (
                        st.session_state.orden_editando.get(
                            "incluir_bus",
                            False
                        )
                    )

                incluir_bus = st.checkbox(
                    "Bus neutro",
                    value=valor_bus
                )

                valor_sensor = False

                if st.session_state.orden_editando:

                    valor_sensor = (
                        st.session_state.orden_editando.get(
                            "incluir_sensor",
                            False
                        )
                    )

                incluir_sensor = st.checkbox(
                    "Sensor neutro",
                    value=valor_sensor
                )

                if incluir_medicion:

                    kits_seleccionados = pd.concat([
                        kits_seleccionados,
                        catalogo.obtener_kits_por_capacidad_y_categoria(
                            capacidad,
                            "Medicion"
                        )
                    ])

                if incluir_bus:

                    kits_seleccionados = pd.concat([
                        kits_seleccionados,
                        catalogo.obtener_kits_por_capacidad_y_categoria(
                            capacidad,
                            "Bus neutro"
                        )
                    ])

                if incluir_sensor:

                    kits_seleccionados = pd.concat([
                        kits_seleccionados,
                        catalogo.obtener_kits_por_capacidad_y_categoria(
                            capacidad,
                            "Sensor neutro"
                        )
                    ])

                st.divider()

            interruptores_izmx = pd.DataFrame()

            mostrar_interruptor_principal = (
                (
                    capacidad == "1600 AMP"
                    and configuracion == "Alimentador"
                )
                or
                (
                    acometida == "Interruptor principal"
                    and montaje
                )
            )

            if configuracion == "Alimentador":

                st.divider()

            if mostrar_interruptor_principal:

                operaciones = [
                    "Manual",
                    "Eléctrica"
                ]

                indice_operacion = None

                if st.session_state.orden_editando:

                    operacion_guardada = (
                        st.session_state.orden_editando.get(
                            "operacion"
                        )
                    )

                    if operacion_guardada in operaciones:

                        indice_operacion = (
                            operaciones.index(
                                operacion_guardada
                            )
                        )

                operacion = st.selectbox(
                    "Operación",
                    operaciones,
                    index=indice_operacion,
                    key="operacion",
                    placeholder="Selecciona una operación"
                )

                montaje_izmx = montaje

                if (
                    capacidad == "1600 AMP"
                    and configuracion == "Alimentador"
                ):
                    montaje_izmx = "Removible"

                if operacion:

                    interruptores_izmx = (
                        catalogo.obtener_interruptores_izmx_filtrados(
                            capacidad,
                            montaje_izmx,
                            operacion
                        )
                    )

                    valor_lsig = False

                    if st.session_state.orden_editando:

                        valor_lsig = (
                            st.session_state.orden_editando.get(
                                "lsig",
                                False
                            )
                        )

                    lsig = st.checkbox(
                        "LSIG",
                        value=valor_lsig
                    )

                    st.divider()

                interruptor_lsig = pd.DataFrame()

                if lsig:

                    interruptor_lsig = (
                        catalogo.obtener_lsig()
                    )

            mostrar_filtro_breakers = (
                (
                    capacidad == "1600 AMP"
                    and configuracion == "Chasis"
                    and (
                        (
                            acometida == "Zapatas principales"
                            and entrada_cables
                        )
                        or (
                            acometida == "Interruptor principal"
                            and operacion
                        )
                    )
                )
                or
                (
                    capacidad in [
                        "2000 AMP",
                        "3200 AMP"
                    ]
                    and acometida == "Interruptor principal"
                    and operacion
                )
                or
                (
                    capacidad in [
                        "2000 AMP",
                        "3200 AMP"
                    ]
                    and acometida in [
                        "Chasis de Derivados",
                        "Secciones Vacías"
                    ]
                    and usar_breakers == "Sí"
                )
            )

            if mostrar_filtro_breakers:

                if acometida in [
                    "Chasis de Derivados",
                    "Secciones Vacías"
                ]:

                    st.divider()

                st.subheader(
                    "Interruptores Derivados"
                )

                marcos = (
                    catalogo.obtener_marcos()
                )

                marco = st.selectbox(
                    "Marco",
                    marcos,
                    index=None,
                    key="marco",
                    placeholder="Selecciona un marco"
                )

                if marco:

                    if marco in imagenes_marco:

                        st.image(
                            imagenes_marco[marco],
                            width="stretch"
                        )

                    tipos = (
                        catalogo.obtener_tipos_por_marco(
                            capacidad,
                            marco
                        )
                    )

                    tipo = st.selectbox(
                        "Tipo",
                        tipos,
                        index=None,
                        key="tipo",
                        placeholder="Selecciona un tipo"
                    )

                    if tipo:

                        breakers = (
                            catalogo.obtener_breakers(
                                capacidad,
                                marco,
                                tipo
                            )
                        )

                        breakers = breakers.copy()

                        breakers["Marco"] = marco

                        if (
                            marco == "PDG"
                            and "Clasificacion" in breakers.columns
                        ):

                            st.session_state.clasificaciones_pdg = (
                                breakers[
                                    [
                                        "Catalogo",
                                        "Clasificacion"
                                    ]
                                ]
                                .drop_duplicates()
                            )

                    st.divider()

            if (
                capacidad == "1600 AMP"
                and configuracion == "Chasis"
            ):

                estructuras = (
                    catalogo.obtener_estructuras_por_capacidad(
                        capacidad
                    )
                )

            elif (
                capacidad in [
                    "2000 AMP",
                    "3200 AMP"
                ]
                and acometida == "Interruptor principal"
            ):

                estructuras = (
                    catalogo.obtener_estructuras_por_capacidad(
                        capacidad
                    )
                )

            if (
                capacidad == "1600 AMP"
                and configuracion == "Alimentador"
            ):

                componentes = (
                    catalogo.obtener_componentes_1600(
                        configuracion
                    )
                )

                componentes = componentes.copy()

                componentes["Cantidad"] = 1

                componentes.loc[
                    componentes["Catalogo"]
                    == "EDSCUBC36",
                    "Cantidad"
                ] = 2

            elif (
                capacidad == "1600 AMP"
                and configuracion == "Chasis"
                and acometida == "Zapatas principales"
            ):

                componentes = (
                    catalogo.obtener_componentes_1600(
                        configuracion,
                        acometida,
                        "Removible"
                    )
                )
            elif (
                capacidad == "1600 AMP"
                and configuracion == "Chasis"
                and acometida
                and montaje
            ):

                componentes = (
                    catalogo.obtener_componentes_1600(
                        configuracion,
                        acometida,
                        montaje
                    )
                )

            elif (
                capacidad in [
                    "2000 AMP",
                    "3200 AMP"
                ]
                and acometida
                and montaje
            ):

                componentes = (
                    catalogo.obtener_componentes_por_acometida(
                        capacidad,
                        acometida,
                        montaje
                    )
                )

            if (
                capacidad in [
                    "2000 AMP",
                    "3200 AMP"
                ]
                and acometida == "Chasis de Derivados"
            ):

                componentes = (
                    catalogo.obtener_derivados(
                        capacidad
                    )
                )

            if (
                capacidad in [
                    "2000 AMP",
                    "3200 AMP"
                ]
                and acometida == "Secciones Vacías"
            ):

                componentes = (
                    catalogo.obtener_secciones_vacias(
                        capacidad
                    )
                )

            if mostrar_filtro_breakers and tipo:

                mostrar_productos(
                    breakers,
                    "breakers",
                    mostrar_boton=True
                )

                tapas = (
                    catalogo.obtener_tapas_por_capacidad(
                        capacidad
                    )
                )

                if not tapas.empty:

                    st.divider()

                    st.subheader(
                        "Tapas"
                    )

                    mostrar_productos(
                        tapas,
                        "tapas",
                        mostrar_boton=True
                    )

    if (
        capacidad == "600 AMP"
        and altura
        and acometida
    ):

        componentes = (
            catalogo.obtener_componentes_por_capacidad_y_acometida(
                capacidad,
                acometida
            )
        )

    if (
        capacidad in [
            "800 AMP",
            "1200 AMP"
        ]
        and altura
        and acometida
    ):

        componentes = (
            catalogo.obtener_componentes_por_capacidad_y_acometida(
                capacidad,
                acometida
            )
        )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Limpiar filtros"):

        st.session_state["limpiar_todo"] = True

        st.rerun()

orden_actual = pd.DataFrame()

total = 0.0

orden_breakers = pd.DataFrame()

orden_tapas = pd.DataFrame()

orden_interruptores = pd.DataFrame()

orden_conectores = pd.DataFrame()

espacio_total = 0

espacio_tapas = 0

espacio_conectores = 0

total_conectores = 0.0

if not st.session_state.carrito_breakers.empty:

    orden_breakers = (
        st.session_state.carrito_breakers.copy()
    )

orden_principal = pd.DataFrame()

if not st.session_state.interruptor_principal.empty:

    orden_principal = (
        st.session_state.interruptor_principal.copy()
    )

if "interruptor_principal" not in st.session_state:

    st.session_state.interruptor_principal = pd.DataFrame()

if not st.session_state.carrito_tapas.empty:

    orden_tapas = (
        st.session_state.carrito_tapas.copy()
    )

if st.session_state.orden_editando:

    capacidad = (
        st.session_state.orden_editando.get(
            "capacidad"
        )
    )

    orden_actual = (
        st.session_state.orden_editando["tablero"]
        .copy()
    )

    orden_breakers = st.session_state.carrito_breakers.copy()

    orden_tapas = st.session_state.carrito_tapas.copy()

    orden_interruptores = (
        st.session_state.orden_editando[
            "interruptores"
        ].copy()
    )

    espacio_total = (
        st.session_state.orden_editando.get(
            "espacio_total",
            0
        )
    )

if (
    "interruptores_izmx" in locals()
    and not interruptores_izmx.empty
    and not st.session_state.orden_editando
):

    orden_interruptores = pd.concat(
        [
            orden_interruptores,
            interruptores_izmx
        ],
        ignore_index=True
    )

if (
    "interruptor_lsig" in locals()
    and not interruptor_lsig.empty
    and not st.session_state.orden_editando
):

    orden_interruptores = pd.concat(
        [
            orden_interruptores,
            interruptor_lsig
        ],
        ignore_index=True
    )

if (
    capacidad
    and not st.session_state.orden_editando
):

    dataframes_orden = []

    if "estructuras" in locals():

        dataframes_orden.append(
            estructuras
        )

    if "componentes" in locals():

        dataframes_orden.append(
            componentes
        )

    if not puerta.empty:

        dataframes_orden.append(
            puerta
        )

    if not kits_seleccionados.empty:

        dataframes_orden.append(
            kits_seleccionados
        )

    if len(dataframes_orden) > 0:

        orden_actual = pd.concat(
            dataframes_orden
        ).drop_duplicates(
            subset=["Catalogo"]
        )

with col2:

    mostrar_espacio = (
        (
            capacidad == "1600 AMP"
            and configuracion == "Chasis"
            and (
                acometida == "Zapatas principales"
                or montaje
            )
        )
        or
        (
            capacidad in [
                "2000 AMP",
                "3200 AMP"
            ]
            and (
                montaje
                or (
                    acometida in [
                        "Chasis de Derivados",
                        "Secciones Vacías"
                    ]
                    and usar_breakers == "Sí"
                )
            )
        )
        or
        (
            capacidad in [
                "600 AMP",
                "800 AMP",
                "1200 AMP"
            ]
            and acometida in [
                "Interruptor principal",
                "Zapatas principales"
            ]
        )
    )

    if mostrar_espacio:

        if acometida in [
            "Chasis de Derivados",
            "Secciones Vacías"
        ]:

            espacio_total = 50

        else:

            if (
                capacidad in [
                    "600 AMP",
                    "800 AMP",
                    "1200 AMP"
                ]
                and altura
            ):

                espacio_total = (
                    catalogo.obtener_espacio_por_capacidad_y_altura(
                        capacidad,
                        altura
                    )
                )

            else:

                espacio_total = (
                    catalogo.obtener_espacio_por_capacidad(
                        capacidad
                    )
                )

        espacio_usado = 0
        espacio_conectores = 0
        st.session_state.espacio_conectores = 0

        espacio_principal = 0

        if (
            capacidad in [
                "600 AMP",
                "800 AMP",
                "1200 AMP"
            ]
            and not st.session_state.interruptor_principal.empty
        ):

            principal = (
                st.session_state.interruptor_principal.iloc[0]
            )

            kit_principal = (
                catalogo.obtener_kits_conectores_para_breaker(
                    capacidad,
                    principal["Marco"],
                    int(principal["# Polos"]),
                    int(principal["Corriente"]),
                    principal.get("Clasificacion")
                )
            )

            if not kit_principal.empty:

                espacio_principal = int(
                    str(
                        kit_principal.iloc[0]["Size"]
                    ).replace("X", "")
                )
            
        espacio_disponible = (
            espacio_total
            - espacio_principal
            - espacio_usado
        )

        st.session_state.espacio_total = espacio_total

        st.session_state.espacio_usado = espacio_usado

        st.session_state.espacio_disponible = espacio_disponible

    if capacidad:

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

        espacio_total = (
            espacio_total_override
            if espacio_total_override is not None
            else obtener_espacio_total(
                catalogo,
                capacidad,
                altura
            )
        )

        espacio_disponible = calcular_espacio_disponible(
            catalogo,
            capacidad,
            altura,
            st.session_state.carrito_breakers,
            st.session_state.carrito_tapas,
            st.session_state.interruptor_principal,
            espacio_total_override
        )

        st.session_state.espacio_total = espacio_total
        st.session_state.espacio_disponible = espacio_disponible

    if st.session_state.ordenes_guardadas:
    
        st.divider()

        st.subheader(
            "Todas las Órdenes"
        )

        for i, orden in enumerate(
            st.session_state.ordenes_guardadas,
            start=1
        ):

            if (
                st.session_state.get("orden_editando_indice")
                == i - 1
            ):
                continue

            with st.expander(
                f"Orden #{i} | ${orden['total']:,.0f}"
            ):

                st.write("Tablero")

                mostrar_productos(
                    orden["tablero"],
                    "orden",
                    mostrar_boton=False
                )

                st.divider()

                col_editar, col_eliminar = st.columns(2)

                with col_editar:

                    if st.button(
                        "Editar",
                        key=f"editar_{i}",
                        width="stretch"
                    ):

                        for key in [
                            "capacidad",
                            "altura",
                            "configuracion",
                            "acometida",
                            "entrada_cables",
                            "montaje",
                            "operacion",
                            "marco",
                            "tipo",
                            "marco_derivado",
                            "marco_derivado_600",
                            "marco_derivado_800",
                            "marco_derivado_1200",
                            "tipo_derivado",
                            "tipo_derivado_600",
                            "tipo_derivado_800",
                            "tipo_derivado_1200"
                        ]:

                            if key in st.session_state:

                                del st.session_state[key]

                        st.session_state.interruptor_principal = (
                            orden.get(
                                "interruptor_principal",
                                pd.DataFrame()
                            ).copy()
                        )

                        st.session_state.carrito_breakers = (
                            orden["breakers"].copy()
                        )

                        st.session_state.carrito_tapas = (
                            orden.get(
                                "tapas",
                                pd.DataFrame()
                            ).copy()
                        )

                        st.session_state.orden_editando = {
                            k: (
                                v.copy()
                                if isinstance(v, pd.DataFrame)
                                else v
                            )
                            for k, v in orden.items()
                        }

                        if orden.get("capacidad") in [
                            "600 AMP",
                            "800 AMP",
                            "1200 AMP"
                        ]:
                            st.session_state.orden_editando[
                                "marco_principal"
                            ] = orden.get(
                                "marco_principal",
                                orden.get("marco")
                            )

                        st.session_state.orden_editando_indice = i - 1

                        st.rerun()

                with col_eliminar:

                    if st.button(
                        "Eliminar",
                        key=f"eliminar_{i}",
                        width="stretch"
                    ):

                        st.session_state.ordenes_guardadas.pop(
                            i - 1
                        )

                        st.rerun()

    st.subheader(
        "Orden Actual"
    )

    if st.session_state.orden_editando:

        st.info(
            "Estás editando una orden guardada"
        )

        st.divider()

    if orden_actual.empty:

        st.info(
            "No hay productos seleccionados"
        )

    else:

        multiplicador_tablero = 1.00

        if not orden_actual.empty:

            multiplicador_tablero = st.number_input(
                "Factor tablero",
                min_value=0.00,
                max_value=1.00,
                value=1.00,
                step=0.01,
                format="%.2f"
            )

            st.caption(
                    f"Precio aplicado: {multiplicador_tablero:.0%}"
                )

        st.subheader(
            "Tablero"
        )

        orden_mostrada = orden_actual.copy()

        orden_mostrada["Precio"] = (
            orden_mostrada["Precio"]
            * multiplicador_tablero
        )

        if "Cantidad" in orden_mostrada.columns:

            orden_mostrada["Precio"] = (
                orden_mostrada["Precio"]
                * orden_mostrada["Cantidad"].fillna(1)
            )

        mostrar_productos(
            orden_mostrada,
            "orden",
            mostrar_boton=False
        )

        principal_mostrado = pd.DataFrame()

        multiplicador_breakers = 1.00

        mostrar_factor_breakers = (
            not orden_interruptores.empty
            or not orden_breakers.empty
            or (
                capacidad in [
                    "600 AMP",
                    "800 AMP",
                    "1200 AMP"
                ]
                and acometida == "Zapatas principales"
            )
        )

        if mostrar_factor_breakers:

            st.divider()

            multiplicador_breakers = st.number_input(
                "Factor breakers",
                min_value=0.00,
                max_value=1.00,
                value=1.00,
                step=0.01,
                format="%.2f",
                key="factor_breakers"
            )

            st.caption(
                f"Precio aplicado: {multiplicador_breakers:.0%}"
            )

        if not orden_principal.empty:

            st.divider()

            st.subheader(
                "Interruptor Principal"
            )

            principal_mostrado = orden_principal.copy()

            principal_mostrado["Precio"] = (
                principal_mostrado["Precio"]
                * multiplicador_breakers
            )

            mostrar_productos(
                principal_mostrado,
                "orden",
                mostrar_boton=False
            )

        breakers_mostrados = pd.DataFrame()

        mostrar_seccion_derivados = (
            mostrar_factor_breakers
            or mostrar_espacio
        )

        if mostrar_seccion_derivados:

            # st.divider()

            st.subheader(
                "Derivados"
            )

            placeholder_espacio = st.empty()

            if mostrar_espacio:

                placeholder_espacio.metric(
                    "Espacio",
                    f"{int(st.session_state.espacio_disponible)}X"
                )

        if not orden_interruptores.empty:

            interruptores_mostrados = (
                orden_interruptores.copy()
            )

            interruptores_mostrados["Precio"] = (
                interruptores_mostrados["Precio"]
                * multiplicador_breakers
            )

            mostrar_productos(
                interruptores_mostrados,
                "orden",
                mostrar_boton=False
            )

        if not orden_breakers.empty:

            breakers_mostrados = (
                orden_breakers
                .groupby(
                    [
                        "Catalogo",
                        "Descripcion",
                        "Precio",
                        "Marco",
                        "Corriente",
                        "# Polos"
                    ],
                    as_index=False
                )
                .size()
            )

            breakers_mostrados.rename(
                columns={
                    "size": "Cantidad"
                },
                inplace=True
            )

            cantidades = (
                orden_breakers["Catalogo"]
                .value_counts()
            )

            breakers_mostrados["Cantidad"] = (
                breakers_mostrados["Catalogo"]
                .map(cantidades)
            )

            breakers_mostrados["Precio"] = (
                breakers_mostrados["Precio"]
                * multiplicador_breakers
            )

            mostrar_productos(
                breakers_mostrados,
                "breakers_orden",
                mostrar_boton=True
            )

        if not orden_tapas.empty:

            st.divider()

            st.subheader(
                "Tapas"
            )

            tapas_mostradas = (
                orden_tapas
                .groupby(
                    [
                        "Catalogo",
                        "Descripcion",
                        "Precio",
                        "Size"
                    ],
                    as_index=False
                )
                .size()
            )

            tapas_mostradas.rename(
                columns={
                    "size": "Cantidad"
                },
                inplace=True
            )

            tapas_mostradas["Precio"] = (
                tapas_mostradas["Precio"]
                * multiplicador_tablero
            )

            for _, tapa in orden_tapas.iterrows():

                size = tapa.get("Size")

                if pd.notna(size):
                    espacio_tapas += int(
                        str(size).replace("X", "")
                    )

            mostrar_productos(
                tapas_mostradas,
                "tapas_orden",
                mostrar_boton=True
            )

        if not orden_breakers.empty:
        
            st.divider()

            st.subheader(
                "Kits de Conectores"
            )

            breakers_resumen = (
                orden_breakers
                .groupby(
                    [
                        "Catalogo",
                        "Marco",
                        "Corriente",
                        "# Polos",
                        "Clasificacion"
                    ],
                    as_index=False
                )
                .size()
            )

            for _, breaker in breakers_resumen.iterrows():

                corriente_texto = str(
                    breaker["Corriente"]
                ).strip()

                if "-" in corriente_texto:

                    corriente = int(
                        corriente_texto
                        .split("-")[1]
                        .strip()
                    )

                else:

                    corriente = int(
                        corriente_texto
                        .replace("A", "")
                        .strip()
                    )

                capacidad_conectores = capacidad

                if capacidad == "600 AMP":

                    capacidad_conectores = "1600 AMP"

                elif capacidad in [
                    "800 AMP",
                    "1200 AMP"
                ]:

                    capacidad_conectores = "2000 AMP"

                kits_conector = (
                    catalogo.obtener_kits_conectores_para_breaker(
                        capacidad_conectores,
                        breaker["Marco"],
                        int(breaker["# Polos"]),
                        corriente,
                        breaker.get("Clasificacion")
                    )
                )

                if kits_conector.empty:
                    st.warning(
                        f"No existe un kit de conectores para {breaker['Catalogo']}."
                    )
                    continue

                st.caption(
                    f"{breaker['Catalogo']} | "
                    f"{breaker['Corriente']}A | "
                    f"{breaker['# Polos']}P | "
                    f"x{breaker['size']}"
                )
                
                opciones = (
                    kits_conector["Ubicacion"]
                    .dropna()
                    .unique()
                    .tolist()
                )

                if len(opciones) > 1:

                    seleccion = st.radio(
                        " ",
                        opciones,
                        horizontal=True,
                        key=f"conector_{breaker['Catalogo']}",
                        label_visibility="collapsed"
                    )

                    kit_seleccionado = (
                        kits_conector[
                            kits_conector["Ubicacion"]
                            == seleccion
                        ]
                        .copy()
                    )

                    kit_seleccionado["Precio"] = (
                        kit_seleccionado["Precio"]
                        * multiplicador_tablero
                    )

                    mostrar_productos(
                        kit_seleccionado,
                        "orden",
                        mostrar_boton=False
                    )

                else:

                    seleccion = opciones[0]

                    st.caption(
                        f"Tipo de conector: {seleccion}"
                    )

                    kit_seleccionado = (
                        kits_conector.copy()
                    )

                    kit_seleccionado["Precio"] = (
                        kit_seleccionado["Precio"]
                        * multiplicador_tablero
                    )

                    mostrar_productos(
                        kit_seleccionado,
                        "orden",
                        mostrar_boton=False
                    )

                cantidad_breakers = int(
                    breaker["size"]
                )

                if seleccion == "Doble":

                    cantidad_kits = (
                        cantidad_breakers + 1
                    ) // 2

                else:

                    cantidad_kits = cantidad_breakers

                total_conectores += (
                    kit_seleccionado["Precio"]
                    .fillna(0)
                    .sum()
                    * cantidad_kits
                )

                size_texto = str(
                    kit_seleccionado.iloc[0]["Size"]
                )

                size_numero = int(
                    size_texto.replace(
                        "X",
                        ""
                    )
                )

                espacio_utilizado = (
                    cantidad_kits
                    * size_numero
                )

                espacio_conectores += espacio_utilizado

                # ...existing code...

                st.session_state.espacio_conectores = (
                    int(espacio_conectores)
                )

                if "espacio_tapas" not in locals():
                    espacio_tapas = 0

                espacio_restante = (
                    espacio_total
                    - espacio_principal
                    - espacio_conectores
                    - espacio_tapas
                )

                st.session_state.espacio_disponible = max(
                    0,
                    int(espacio_restante)
                )

                placeholder_espacio.metric(
                    "Espacio",
                    f"{int(st.session_state.espacio_disponible)}X"
                )

                st.markdown(
                    f"""
                    <div class="espacio-flotante">
                        <div style="font-size:12px">
                            ESPACIO
                        </div>
                        <div style="font-size:28px">
                            {int(st.session_state.espacio_disponible)}X
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
                st.markdown(
                    """
                    <style>
            
                    .espacio-flotante {
                    position: fixed;
                    top: 90px;
                    right: 20px;
                    z-index: 9999;
            
                    background-color: #005EB8;
                    color: white;
            
                    padding: 14px 18px;
            
                    border-radius: 12px;
            
                    font-size: 18px;
                    text-align: center;
                    font-weight: 700;
            
                    box-shadow: 0 4px 12px rgba(0,0,0,.30);
                }
            
                    </style>
                    """,
                    unsafe_allow_html=True
                )

        if "Cantidad" not in orden_mostrada.columns:

            orden_mostrada["Cantidad"] = 1

        orden_mostrada["Cantidad"] = (
            orden_mostrada["Cantidad"]
            .fillna(1)
        )

        total += (
            orden_mostrada["Precio"]
            .fillna(0)
            .sum()
        )

        if not orden_principal.empty:
            total += (
                principal_mostrado["Precio"]
                .fillna(0)
                .sum()
            )
            
        if not orden_tapas.empty:

            total += (
                tapas_mostradas["Precio"]
                .mul(tapas_mostradas["Cantidad"].fillna(1))
                .fillna(0)
                .sum()
            )

        if not orden_interruptores.empty:

            total += (
                interruptores_mostrados["Precio"]
                .sum()
            )

        if not orden_breakers.empty:

            total += (
                breakers_mostrados["Precio"]
                .mul(breakers_mostrados["Cantidad"].fillna(1))
                .sum()
            )

        total += total_conectores

        st.divider()

        st.metric(
            "Total",
            f"${total:,.0f}"
        )

        st.divider()

        col_guardar, col_nueva = st.columns(2)

        with col_guardar:

            if st.button(
                "Guardar orden",
                width="stretch"
            ):

                orden_guardada = {
                    "tablero": orden_actual.copy(),
                    "interruptor_principal": (
                        st.session_state.interruptor_principal.copy()
                    ),
                    "breakers": orden_breakers.copy(),
                    "tapas": orden_tapas.copy(),
                    "interruptores": orden_interruptores.copy(),
                    "capacidad": capacidad,
                    "altura": altura,
                    "configuracion": configuracion,
                    "acometida": acometida,
                    "entrada_cables": entrada_cables,
                    "incluir_medicion": incluir_medicion,
                    "incluir_bus": incluir_bus,
                    "incluir_sensor": incluir_sensor,
                    "operacion": operacion,
                    "lsig": lsig,
                    "marco": marco,
                    "marco_principal": (
                        marco
                        if capacidad in [
                            "600 AMP",
                            "800 AMP",
                            "1200 AMP"
                        ]
                        else None
                    ),
                    "tipo": tipo,
                    "montaje": montaje,
                    "espacio_total": espacio_total,
                    "total": total
                }

                indice_edicion = st.session_state.get(
                    "orden_editando_indice"
                )

                if (
                    indice_edicion is not None
                    and indice_edicion < len(
                        st.session_state.ordenes_guardadas
                    )
                ):
                    st.session_state.ordenes_guardadas[
                        indice_edicion
                    ] = orden_guardada
                else:
                    st.session_state.ordenes_guardadas.append(
                        orden_guardada
                    )

                st.session_state.orden_editando = None
                st.session_state.orden_editando_indice = None

                st.toast(
                    "✅ Orden guardada"
                )

                st.rerun()


        with col_nueva:

            if st.button(
                "Nueva orden",
                width="stretch"
            ):

                st.session_state.orden_editando = None
                st.session_state.orden_editando_indice = None

                st.session_state["limpiar_todo"] = True

                st.rerun()