# Librerías
# Instalar con:
# pip install shiny shinywidgets faicons plotly pandas statsmodels
import socket
from pathlib import Path
from typing import Any

import faicons as fa
import pandas as pd
import plotly.express as px  # type: ignore[import-not-found]

from shiny import App, reactive, render, ui
from shinywidgets import output_widget, render_plotly

# Directorio base de la aplicación
app_dir = Path(__file__).parent

# ---------------------------------------------------------------------------
# Carga y preparación de los datos
# ---------------------------------------------------------------------------

# Carga el dataset y traduce nombres de columnas al español
datos = pd.read_csv(app_dir / "tips.csv").rename(
    columns={
        "total_bill": "cuenta_total",
        "tip": "propina",
        "sex": "genero",
        "smoker": "fumador",
        "day": "dia",
        "time": "turno",
        "size": "comensales",
    }
)

# Traduce las categorías de cada columna al español
datos["genero"] = datos["genero"].map({"Male": "Hombre", "Female": "Mujer"})
datos["fumador"] = datos["fumador"].map({"Yes": "Sí", "No": "No"})
datos["turno"] = datos["turno"].map({"Lunch": "Almuerzo", "Dinner": "Cena"})

orden_dias = ["Jueves", "Viernes", "Sábado", "Domingo"]
datos["dia"] = datos["dia"].map(
    {"Thur": "Jueves", "Fri": "Viernes", "Sat": "Sábado", "Sun": "Domingo"}
)
datos["dia"] = pd.Categorical(datos["dia"], categories=orden_dias, ordered=True)

# Columna calculada: porcentaje de propina sobre la cuenta total
datos["porcentaje_propina"] = (datos["propina"] / datos["cuenta_total"]) * 100

# Rango de la cuenta total, usado para el control deslizante
rango_cuenta = (datos["cuenta_total"].min(), datos["cuenta_total"].max())

# ---------------------------------------------------------------------------
# Paleta de colores y estilo de las gráficas
# ---------------------------------------------------------------------------

PALETA = {
    "azul": "#2563EB",
    "teal": "#0D9488",
    "morado": "#7C3AED",
    "naranja": "#F59E0B",
    "rojo": "#DC2626",
    "gris": "#64748B",
}

SECUENCIA_COLORES = [PALETA["azul"], PALETA["teal"], PALETA["naranja"], PALETA["morado"]]

# Opciones disponibles para colorear el gráfico de dispersión
OPCIONES_COLOR: dict[str, str | None] = {
    "Ninguno": None,
    "Género": "genero",
    "Fumador": "fumador",
    "Día": "dia",
    "Turno": "turno",
}

# Estilos personalizados de la aplicación (tipografía, tarjetas e indicadores)
ESTILOS = ui.tags.style(
    """
    body {
        font-family: 'Inter', -apple-system, sans-serif;
        background-color: #F1F5F9;
    }
    .card {
        border: none;
        border-radius: 16px;
        box-shadow: 0 2px 12px rgba(15, 23, 42, 0.08);
        margin-bottom: 1rem;
    }
    .card-header {
        font-weight: 600;
        background-color: #ffffff;
        border-bottom: 1px solid #E2E8F0;
    }
    .descripcion-grafico {
        color: #64748B;
        font-size: 0.85rem;
        margin: 0.4rem 0 0.6rem 0;
    }
    .seccion-titulo {
        margin: 1.2rem 0 0.6rem 0;
        font-weight: 700;
        color: #1E293B;
    }
    .tarjeta-contexto {
        background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 55%, #7C3AED 100%);
        color: #ffffff;
        border-radius: 16px;
    }
    .tarjeta-contexto p, .tarjeta-contexto li {
        color: #E2E8F0;
    }
    .tarjeta-contexto h3 {
        color: #ffffff;
        font-weight: 700;
    }
    /* Ajustes de tamaño para que los indicadores no se vean recortados */
    .value-box-showcase svg {
        height: 2.3rem !important;
        width: 2.3rem !important;
    }
    .value-box-title p {
        font-size: 0.85rem;
        margin: 0;
        opacity: 0.95;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    .value-box-value p {
        font-size: 1.7rem;
        margin: 0;
        font-weight: 700;
    }
    .sidebar {
        max-height: 100vh;
        overflow-y: auto;
    }
    """
)

ENCABEZADO = ui.head_content(
    ui.tags.link(
        rel="stylesheet",
        href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap",
    ),
    ESTILOS,
)

# ---------------------------------------------------------------------------
# Interfaz de usuario (UI)
# ---------------------------------------------------------------------------

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_slider(
            "cuenta_total",
            "Rango de cuenta total",
            min=rango_cuenta[0],
            max=rango_cuenta[1],
            value=rango_cuenta,
            pre="$",
        ),
        ui.input_checkbox_group(
            "turno",
            "Turno",
            ["Almuerzo", "Cena"],
            selected=["Almuerzo", "Cena"],
            inline=True,
        ),
        ui.input_checkbox_group(
            "genero",
            "Género",
            ["Hombre", "Mujer"],
            selected=["Hombre", "Mujer"],
            inline=True,
        ),
        ui.input_checkbox_group(
            "fumador",
            "Fumador",
            ["Sí", "No"],
            selected=["Sí", "No"],
            inline=True,
        ),
        ui.input_checkbox_group(
            "dia",
            "Día de la semana",
            orden_dias,
            selected=orden_dias,
        ),
        ui.input_action_button(
            "reiniciar", "Restablecer filtros", class_="btn-outline-secondary"
        ),
        width=300,
    ),
    ENCABEZADO,
    # Tarjeta de contexto: explica de qué trata el tablero
    ui.card(
        ui.card_header("Acerca de este tablero"),
        ui.div(
            ui.h3("Análisis de propinas en un restaurante"),
            ui.markdown(
                """
Este tablero explora el dataset **`tips`** (244 cuentas registradas en un
restaurante), usado como caso de estudio.

Cada fila representa una cuenta individual e incluye el monto total, la
propina dejada, el género y hábito de fumar del cliente que pagó, el día
y turno de la visita, y el número de comensales en la mesa.

Esto nos permite identificar patrones que apoyen decisiones de negocio,
como en qué días/turnos reforzar personal, o qué grupos de clientes
tienden a dejar mejores propinas.
                """
            ),
            class_="tarjeta-contexto p-4",
        ),
    ),
    # Indicadores principales
    ui.layout_columns(
        ui.value_box(
            "Total de clientes",
            ui.output_ui("total_clientes"),
            showcase=fa.icon_svg("users"),
            showcase_layout="top right",
            theme="bg-gradient-blue-purple",
            height="130px",
        ),
        ui.value_box(
            "Cuenta promedio",
            ui.output_ui("cuenta_promedio"),
            showcase=fa.icon_svg("dollar-sign"),
            showcase_layout="top right",
            theme="bg-gradient-teal-blue",
            height="130px",
        ),
        ui.value_box(
            "Propina promedio",
            ui.output_ui("propina_promedio"),
            showcase=fa.icon_svg("percent"),
            showcase_layout="top right",
            theme="bg-gradient-orange-red",
            height="130px",
        ),
        ui.value_box(
            "Propinas acumuladas",
            ui.output_ui("propina_total"),
            showcase=fa.icon_svg("wallet"),
            showcase_layout="top right",
            theme="bg-gradient-purple-blue",
            height="130px",
        ),
    ),
    # Sección: relación entre cuenta y propina
    ui.h5("Relación entre la cuenta y la propina", class_="seccion-titulo"),
    ui.layout_columns(
        ui.card(
            ui.card_header(
                "Cuenta total vs. propina",
                ui.popover(
                    fa.icon_svg("ellipsis"),
                    ui.input_radio_buttons(
                        "color_dispersion",
                        "Colorear por:",
                        list(OPCIONES_COLOR.keys()),
                        inline=True,
                    ),
                    title="Variable de color",
                    placement="top",
                ),
            ),
            ui.p(
                "Cada punto representa una cuenta. La línea muestra la tendencia "
                "general entre el monto de la cuenta y la propina dejada.",
                class_="descripcion-grafico",
            ),
            output_widget("grafico_dispersion", height="380px"),
            full_screen=True,
        ),
        ui.card(
            ui.card_header("Distribución del monto de las cuentas"),
            ui.p(
                "Frecuencia con la que se repiten distintos rangos de cuenta "
                "total, útil para identificar el ticket promedio típico.",
                class_="descripcion-grafico",
            ),
            output_widget("grafico_histograma", height="380px"),
        ),
        col_widths=[7, 5],
    ),
    # Sección: comportamiento por día y turno
    ui.h5("Comportamiento por día y turno", class_="seccion-titulo"),
    ui.layout_columns(
        ui.card(
            ui.card_header("Propina promedio por día"),
            ui.p(
                "Compara cuánto dejan de propina, en promedio, los clientes según "
                "el día de la semana en que visitan el restaurante.",
                class_="descripcion-grafico",
            ),
            output_widget("grafico_barras_dia", height="340px"),
        ),
        ui.card(
            ui.card_header("Distribución de la propina por turno"),
            ui.p(
                "Qué tan dispersas son las propinas en el almuerzo frente a la "
                "cena, incluyendo la mediana y posibles valores atípicos.",
                class_="descripcion-grafico",
            ),
            output_widget("grafico_caja_turno", height="340px"),
        ),
    ),
    ui.layout_columns(
        ui.card(
            ui.card_header("Porcentaje de propina promedio por día y turno"),
            ui.p(
                "Mapa de calor que resalta en qué combinación de día y turno se "
                "deja, en promedio, un mejor porcentaje de propina.",
                class_="descripcion-grafico",
            ),
            output_widget("grafico_mapa_calor", height="320px"),
        ),
    ),
    # Sección: perfil de los clientes
    ui.h5("Perfil de los clientes", class_="seccion-titulo"),
    ui.layout_columns(
        ui.card(
            ui.card_header("Clientes por género"),
            ui.p(
                "Proporción de hombres y mujeres dentro del grupo de datos "
                "filtrado.",
                class_="descripcion-grafico",
            ),
            output_widget("grafico_dona_genero", height="300px"),
        ),
        ui.card(
            ui.card_header("Clientes fumadores vs. no fumadores"),
            ui.p(
                "Proporción de clientes que fuman frente a los que no.",
                class_="descripcion-grafico",
            ),
            output_widget("grafico_dona_fumador", height="300px"),
        ),
        ui.card(
            ui.card_header("Propina según el tamaño del grupo"),
            ui.p(
                "Porcentaje de propina promedio según el número de comensales "
                "en la mesa: los grupos pequeños suelen dejar un porcentaje "
                "mayor.",
                class_="descripcion-grafico",
            ),
            output_widget("grafico_barras_comensales", height="300px"),
        ),
    ),
    # Tabla de datos
    ui.h5("Detalle de las cuentas", class_="seccion-titulo"),
    ui.card(
        ui.card_header("Datos filtrados"),
        ui.p(
            "Datos individuales de cada cuenta según los filtros seleccionados.",
            class_="descripcion-grafico",
        ),
        ui.output_data_frame("tabla_datos"),
        full_screen=True,
    ),
    title="Tablero de propinas del restaurante",
    fillable=False,
)


# ---------------------------------------------------------------------------
# Lógica del servidor
# ---------------------------------------------------------------------------

def server(input: Any, output: Any, session: Any):
    # Aplica todos los filtros del sidebar sobre el conjunto de datos completo
    @reactive.calc
    def datos_filtrados():
        cuenta = input.cuenta_total()
        return datos[
            (datos["cuenta_total"].between(cuenta[0], cuenta[1]))
            & (datos["turno"].isin(input.turno()))
            & (datos["genero"].isin(input.genero()))
            & (datos["fumador"].isin(input.fumador()))
            & (datos["dia"].isin(input.dia()))
        ]

    # Indicadores (value boxes)
    @render.ui
    def total_clientes():
        return f"{datos_filtrados().shape[0]}"

    @render.ui
    def cuenta_promedio():
        promedio = datos_filtrados()["cuenta_total"].mean()
        return f"${promedio:.2f}" if pd.notna(promedio) else "N/A"

    @render.ui
    def propina_promedio():
        promedio = datos_filtrados()["porcentaje_propina"].mean()
        return f"{promedio:.1f}%" if pd.notna(promedio) else "N/A"

    @render.ui
    def propina_total():
        total = datos_filtrados()["propina"].sum()
        return f"${total:,.2f}"

# Gráfico de dispersión: cuenta total vs propina
    @render_plotly
    def grafico_dispersion():
        variable_color = OPCIONES_COLOR.get(input.color_dispersion(), None)
        figura = px.scatter(
            datos_filtrados(),
            x="cuenta_total",
            y="propina",
            color=variable_color,
            trendline="ols",  # <--- CAMBIAR "lowess" POR "ols" (o quitar la línea si prefieres)
            template="plotly_white",
            color_discrete_sequence=SECUENCIA_COLORES,
            labels={"cuenta_total": "Cuenta total ($)", "propina": "Propina ($)"},
        )
        figura.update_layout(margin=dict(l=10, r=10, t=10, b=10), legend_title_text="")
        return figura

    # Histograma: distribución del monto de las cuentas
    @render_plotly
    def grafico_histograma():
        figura = px.histogram(
            datos_filtrados(),
            x="cuenta_total",
            nbins=20,
            template="plotly_white",
            color_discrete_sequence=[PALETA["azul"]],
            labels={"cuenta_total": "Cuenta total ($)"},
        )
        figura.update_layout(
            margin=dict(l=10, r=10, t=10, b=10), yaxis_title="Número de cuentas"
        )
        return figura

    # Gráfico de barras: propina promedio por día de la semana
    @render_plotly
    def grafico_barras_dia():
        resumen = (
            datos_filtrados()
            .groupby("dia", observed=False)["propina"]
            .mean()
            .reindex(orden_dias)
            .reset_index()
        )
        figura = px.bar(
            resumen,
            x="dia",
            y="propina",
            color="dia",
            template="plotly_white",
            color_discrete_sequence=SECUENCIA_COLORES,
            labels={"dia": "Día", "propina": "Propina promedio ($)"},
        )
        figura.update_layout(showlegend=False, margin=dict(l=10, r=10, t=10, b=10))
        return figura

    # Gráfico de caja: distribución de la propina por turno
    @render_plotly
    def grafico_caja_turno():
        figura = px.box(
            datos_filtrados(),
            x="turno",
            y="propina",
            color="turno",
            points="all",
            template="plotly_white",
            color_discrete_sequence=SECUENCIA_COLORES,
            labels={"turno": "Turno", "propina": "Propina ($)"},
        )
        figura.update_layout(showlegend=False, margin=dict(l=10, r=10, t=10, b=10))
        return figura

    # Mapa de calor: porcentaje de propina promedio por día y turno
    @render_plotly
    def grafico_mapa_calor():
        tabla = (
            datos_filtrados()
            .pivot_table(
                index="dia",
                columns="turno",
                values="porcentaje_propina",
                aggfunc="mean",
                observed=False,
            )
            .reindex(orden_dias)
            .reindex(columns=["Almuerzo", "Cena"])
            .fillna(0)
        )
        figura = px.imshow(
            tabla,
            text_auto=".1f",
            color_continuous_scale="Blues",
            template="plotly_white",
            labels=dict(x="Turno", y="Día", color="% Propina"),
        )
        figura.update_layout(margin=dict(l=10, r=10, t=10, b=10))
        return figura

    # Gráfico de dona: proporción de clientes por género
    @render_plotly
    def grafico_dona_genero():
        conteo = datos_filtrados()["genero"].value_counts().reset_index()
        conteo.columns = ["genero", "clientes"]
        figura = px.pie(
            conteo,
            names="genero",
            values="clientes",
            hole=0.55,
            color="genero",
            template="plotly_white",
            color_discrete_map={"Hombre": PALETA["azul"], "Mujer": PALETA["morado"]},
        )
        figura.update_traces(textinfo="percent+label")
        figura.update_layout(margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
        return figura

    # Gráfico de dona: proporción de clientes fumadores vs no fumadores
    @render_plotly
    def grafico_dona_fumador():
        conteo = datos_filtrados()["fumador"].value_counts().reset_index()
        conteo.columns = ["fumador", "clientes"]
        figura = px.pie(
            conteo,
            names="fumador",
            values="clientes",
            hole=0.55,
            color="fumador",
            template="plotly_white",
            color_discrete_map={"Sí": PALETA["naranja"], "No": PALETA["teal"]},
        )
        figura.update_traces(textinfo="percent+label")
        figura.update_layout(margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
        return figura

    # Gráfico de barras: porcentaje de propina promedio por número de comensales
    @render_plotly
    def grafico_barras_comensales():
        resumen = (
            datos_filtrados()
            .groupby("comensales")["porcentaje_propina"]
            .mean()
            .reset_index()
            .sort_values("comensales")
        )
        figura = px.bar(
            resumen,
            x="comensales",
            y="porcentaje_propina",
            template="plotly_white",
            color_discrete_sequence=[PALETA["teal"]],
            labels={
                "comensales": "Número de comensales",
                "porcentaje_propina": "Propina promedio (%)",
            },
        )
        figura.update_layout(margin=dict(l=10, r=10, t=10, b=10))
        return figura

    # Tabla con el detalle de las cuentas filtradas
    @render.data_frame
    def tabla_datos():
        return render.DataGrid(datos_filtrados(), filters=True)

    # Restablece todos los filtros a sus valores iniciales
    @reactive.effect
    @reactive.event(input.reiniciar)
    def _():
        ui.update_slider("cuenta_total", value=rango_cuenta)
        ui.update_checkbox_group("turno", selected=["Almuerzo", "Cena"])
        ui.update_checkbox_group("genero", selected=["Hombre", "Mujer"])
        ui.update_checkbox_group("fumador", selected=["Sí", "No"])
        ui.update_checkbox_group("dia", selected=orden_dias)


app = App(app_ui, server)


def get_free_port(start_port: int = 8002, end_port: int = 9000) -> int:
    for port in range(start_port, end_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError("No hay puertos disponibles entre 8002 y 9000")


if __name__ == "__main__":
    port = get_free_port()
    print(f"Dashboard funcionando en http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port)