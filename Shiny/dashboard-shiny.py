# Librerias
# Instalar con:
# pip install shiny shinywidgets faicons plotly pandas statsmodels
from pathlib import Path
import faicons as fa
import plotly.express as px
import pandas as pd

from shiny import App, reactive, render, ui
from shinywidgets import output_widget, render_plotly

# directorio de la app
app_dir = Path(__file__).parent

# cargar los datos del tablero
tips = pd.read_csv(app_dir / "tips.csv")

bill_rng = (
    tips["total_bill"].min(),
    tips["total_bill"].max()
)

# UI (Interfaz de usuario)
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_slider(
            "total_bill",
            "Bill amount",
            min=bill_rng[0],
            max=bill_rng[1],
            value=bill_rng,
            pre="$",
        ),
        ui.input_checkbox_group(
            "time",
            "Food service",
            ["Lunch", "Dinner"],
            selected=["Lunch", "Dinner"],
            inline=True,
        ),
        # Fix: el argumento correcto es class_ (guion bajo al final), no _class
        ui.input_action_button("reset", "Reset filter", class_="btn-outline-secondary")
    ),
    # Fila de Value Boxes
    ui.layout_columns(
        ui.value_box(
            "Total tippers", ui.output_ui("total_tippers"), showcase=fa.icon_svg("user", "regular")
        ),
        ui.value_box(
            "Average bill", ui.output_ui("average_bill"),  showcase=fa.icon_svg("dollar-sign")
        )
    ),
    # Fila de Tabla y Gráfico
    ui.layout_columns(
        ui.card(
            ui.card_header("Tips data"), ui.output_data_frame("table"), full_screen=True
        ),
        ui.card(
            ui.card_header(
                "Total bill vs tip",
                ui.popover(
                    fa.icon_svg("ellipsis"),
                    ui.input_radio_buttons(
                        "scatter_color",
                        None,
                        ["none", "sex", "smoker", "day", "time"],
                        inline=True,
                    ),
                    title="Add a color variable",
                    placement="top",
                ),
            ),
            output_widget("scatterplot")
        )
    ),
    title="Restaurant tipping",
    fillable=True
)

# Server (Lógica)
def server(input, output, session):
    @reactive.calc
    def tips_data():
        bill = input.total_bill()
        return tips[
                    (tips["total_bill"].between(bill[0], bill[1])) &
                    (tips["time"].isin(input.time()))
                ]

    @render.ui
    def total_tippers():
        return tips_data().shape[0]

    @render.ui
    def average_bill():
        d = tips_data()["total_bill"].mean()
        # Fix: pd.notna() en vez de "if d" para detectar bien el caso sin datos (NaN)
        if pd.notna(d):
            return f"${d:.2f}"
        else:
            return "N/A"

    @render.data_frame
    def table():
        return render.DataGrid(tips_data())

    @render_plotly
    def scatterplot():
        color = input.scatter_color()
        return px.scatter(
            tips_data(),
            x="total_bill",
            y="tip",
            color=None if color == "none" else color,
            trendline="lowess",
        )

    @reactive.effect
    @reactive.event(input.reset)
    def _():
        ui.update_slider("total_bill", value=bill_rng)
        ui.update_checkbox_group("time", selected=["Lunch", "Dinner"])

app = App(app_ui, server)

if __name__ == "__main__":
    app.run()