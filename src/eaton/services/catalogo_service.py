# services/catalogo_service.py

import pandas as pd

class CatalogoService:

    def __init__(self, archivo):

        self.archivo = archivo

        self.hojas = pd.read_excel(
            archivo,
            sheet_name=None
        )

    def obtener_hoja(
        self,
        nombre
    ):

        return self.hojas[nombre]


    def obtener_estructura(self):
        return self.hojas["Estructura"]

    def obtener_1600(self):
        return self.hojas["1600 AMP"]

    def obtener_2000(self):
        return self.hojas["2000 AMP"]

    def obtener_3200(self):
        return self.hojas["3200 AMP"]

    def obtener_conectores(self):
        return self.hojas["Conectores"]

    def obtener_tapas(self):
        return self.hojas["Tapas"]

    def obtener_kits(self):
        return self.hojas["Kits"]

    def obtener_hoja_marco(self, marco):
        return self.hojas[marco]

    def obtener_estructuras_por_capacidad(
        self,
        capacidad
    ):

        estructuras = self.obtener_estructura()

        return estructuras[
            estructuras["Capacidad"] == capacidad
        ]

    def obtener_alturas_por_capacidad(
        self,
        capacidad
    ):

        estructuras = self.obtener_estructura()

        alturas = (
            estructuras[
                estructuras["Capacidad"] == capacidad
            ]["Altura"]
            .dropna()
            .unique()
        )

        return sorted([int(x) for x in alturas])


    def obtener_estructura_por_capacidad_y_altura(
        self,
        capacidad,
        altura
    ):

        estructuras = self.obtener_estructura()

        return estructuras[
            (estructuras["Capacidad"] == capacidad)
            &
            (estructuras["Altura"] == altura)
        ]

    def obtener_configuraciones_1600(self):

        configuraciones = (
            self.obtener_1600()["Configuracion"]
            .dropna()
            .unique()
        )

        return sorted(configuraciones)

    def obtener_componentes_1600_por_configuracion(
        self,
        configuracion
    ):

        componentes = self.obtener_1600()

        return componentes[
            componentes["Configuracion"]
            == configuracion
        ]

    def obtener_acometidas_1600(
        self,
        configuracion
    ):

        df = self.obtener_1600()

        acometidas = (
            df[
                df["Configuracion"]
                == configuracion
            ]["Acometida"]
            .dropna()
            .unique()
        )

        return sorted(acometidas)

    def obtener_acometidas_por_capacidad(
        self,
        capacidad
    ):

        hoja = self.obtener_hoja(
            capacidad
        )

        acometidas = (
            hoja["Acometida"]
            .dropna()
            .unique()
        )

        return sorted(acometidas)

    def obtener_componentes_por_capacidad_y_acometida(
        self,
        capacidad,
        acometida
    ):

        hoja = self.obtener_hoja(
            capacidad
        )

        return hoja[
            hoja["Acometida"]
            == acometida
        ]

    def obtener_componentes_1600(
        self,
        configuracion,
        acometida=None,
        montaje=None
    ):

        df = self.obtener_1600()

        if configuracion == "Alimentador":

            return df[
                df["Configuracion"] == configuracion
            ]

        return df[
            (df["Configuracion"] == configuracion)
            &
            (df["Acometida"] == acometida)
            &
            (df["Montaje"] == montaje)
        ]

    def obtener_componentes_por_acometida(
        self,
        capacidad,
        acometida,
        montaje
    ):

        hoja = self.obtener_hoja(
            capacidad
        )

        return hoja[
            (hoja["Acometida"] == acometida)
            &
            (hoja["Montaje"] == montaje)
        ]

    def obtener_montajes_1600(
        self,
        configuracion,
        acometida=None
    ):

        df = self.obtener_1600()

        montajes = (
            df[
                (df["Configuracion"] == configuracion)
                &
                (df["Acometida"] == acometida)
            ]["Montaje"]
            .dropna()
            .unique()
        )

        return sorted(montajes)

    def obtener_montajes_por_capacidad(
        self,
        capacidad,
        acometida
    ):

        hoja = self.obtener_hoja(
            capacidad
        )

        montajes = (
            hoja[
                hoja["Acometida"] == acometida
            ]["Montaje"]
            .dropna()
            .unique()
        )

        return sorted(montajes)

    def obtener_medicion(self):

        kits = self.obtener_kits()

        return kits[
            kits["Categoria"] == "Medicion"
        ]

    def obtener_kits(self):

        return self.hojas["Kits"]

    def obtener_kits_neutro(self):

        kits = self.obtener_kits()

        return kits[
            kits["Categoria"] == "Kit"
        ]

    def obtener_kits_por_capacidad_y_categoria(
        self,
        capacidad,
        categoria
    ):

        kits = self.obtener_kits()

        return kits[
            (kits["Capacidad"] == capacidad)
            &
            (kits["Categoria"] == categoria)
        ]

    def obtener_marcos(self):

        return [
            "BZM",
            "PDG",
            "F",
            "J",
            "K",
            "L"
        ]

    def obtener_tipos_por_marco(
        self,
        capacidad,
        marco
    ):

        hoja = self.obtener_hoja(
            marco
        )

        tipos = (
            hoja["Tipo"]
            .dropna()
            .unique()
        )

        if (
            capacidad == "1600 AMP"
            and marco == "PDG"
        ):

            hoja = hoja[
                hoja["Clasificacion"]
                .isin(
                    [
                        "PDG2",
                        "PDG3"
                    ]
                )
            ]

            tipos = (
                hoja["Tipo"]
                .dropna()
                .unique()
            )

        return sorted(tipos)

    def obtener_breakers(
        self,
        capacidad,
        marco,
        tipo
    ):

        hoja = self.obtener_hoja(
            marco
        )

        breakers = hoja[
            hoja["Tipo"] == tipo
        ]

        if (
            capacidad == "1600 AMP"
            and marco == "PDG"
        ):

            breakers = breakers[
                breakers["Clasificacion"]
                .isin(
                    [
                        "PDG2",
                        "PDG3"
                    ]
                )
            ]

        return breakers

    def obtener_espacio_por_capacidad(
        self,
        capacidad
    ):

        estructura = self.obtener_estructuras_por_capacidad(
            capacidad
        )

        espacio_texto = str(
            estructura.iloc[0]["Espacio"]
        )

        espacio_numero = int(
            espacio_texto
            .replace("X", "")
            .replace(" ", "")
        )

        return espacio_numero

    def obtener_componentes_600(
        self
    ):

        df = self.obtener_1600()

        return df

    def obtener_componentes_800_1200(
        self,
        montaje
    ):

        df = self.obtener_2000()

        return df[
            df["Montaje"] == montaje
        ]

    def obtener_interruptores_izmx(self):

        return self.hojas[
            "Interruptores IZMX"
        ]

    def obtener_interruptores_izmx_filtrados(
        self,
        capacidad,
        montaje,
        operacion
    ):

        df = self.obtener_interruptores_izmx()

        capacidad_num = int(
            capacidad.split()[0]
        )

        df = df[
            (df["Capacidad"] == capacidad_num)
            &
            (df["Montaje"] == montaje)
            &
            (df["Tipo"] == operacion)
        ].copy()

        df["Descripcion"] = (
            "Interruptor IZMX "
            + df["Tipo"]
        )

        return df

    def obtener_lsig(self):

        df = self.obtener_interruptores_izmx()

        df = df[
            df["Catalogo"]
            == "+IZMX-PXRP-T-1"
        ].copy()

        df["Descripcion"] = (
            "PRX25 Falla a Tierra LSIG"
        )

        return df

    def obtener_puerta_por_entrada(
        self,
        entrada_cables
    ):

        df = self.hojas["Puertas"]

        return df[
            df["Entrada de cables"]
            == entrada_cables
        ]

    def obtener_derivados(
        self,
        capacidad
    ):

        df = self.hojas["Derivados"]

        return df[
            df["Capacidad"] == capacidad
        ]

    def obtener_secciones_vacias(
        self,
        capacidad
    ):

        df = self.hojas["SV"]

        return df[
            df["Capacidad"] == capacidad
        ]

    def obtener_kits_conectores_para_breaker(
        self,
        capacidad,
        marco,
        polos,
        corriente,
        clasificacion=None
    ):

        df = self.hojas["Conectores"].copy()

        candidatos = df[
            (df["Capacidad"] == capacidad)
            &
            (df["Marco"] == marco)
            &
            (df["Corriente Min"] <= corriente)
            &
            (df["Corriente Max"] >= corriente)
        ]

        def coincide_polos(valor):

            valor = str(valor)

            if "-" in valor:

                minimo, maximo = valor.split("-")

                return (
                    int(minimo)
                    <= polos
                    <= int(maximo)
                )

            return int(valor) == polos

        candidatos = candidatos[
            candidatos["# Polos"]
            .apply(coincide_polos)
        ]

        if (
            marco == "PDG"
            and clasificacion is not None
            and "Clasificacion" in candidatos.columns
        ):

            candidatos = candidatos[
                candidatos["Clasificacion"]
                == clasificacion
            ]

        return candidatos

    def obtener_tapas_por_capacidad(
        self,
        capacidad
    ):

        df = self.obtener_tapas()

        return df[
            df["Capacidad"] == capacidad
        ]

    def obtener_espacio_por_capacidad_y_altura(
        self,
        capacidad,
        altura
    ):

        estructura = (
            self.obtener_estructura_por_capacidad_y_altura(
                capacidad,
                altura
            )
        )

        espacio_texto = str(
            estructura.iloc[0]["Espacio"]
        )

        espacio_numero = int(
            espacio_texto
            .replace("X", "")
            .replace(" ", "")
        )

        return espacio_numero

    def obtener_x_breaker(
        self,
        capacidad,
        marco,
        polos,
        corriente
    ):

        kit = self.obtener_kits_conectores_para_breaker(
            capacidad,
            marco,
            polos,
            corriente
        )

        if kit.empty:
            return 0

        return int(
            str(
                kit.iloc[0]["Size"]
            ).replace("X", "")
        )