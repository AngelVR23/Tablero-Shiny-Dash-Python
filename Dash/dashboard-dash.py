import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output, State, dash_table, callback
import dash_bootstrap_components as dbc
from pathlib import Path

# Cargar datos
app_dir = Path(__file__).parent
tips = pd.read_csv(app_dir / "tips.csv")

bill_min = tips["total_bill"].min()
bill_max = tips["total_bill"].max()

# Inicializar App con tema Bootstrap
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME])

# Layout (UI)
app.layout = dbc.Container([
    html.H1("Restaurant tipping", className="my-3"),
    
    dbc.Row([
        # Sidebar
        dbc.Col([
            html.Div([
                html.Label("Bill amount"),
                dcc.RangeSlider(
                    id="total_bill",
                    min=bill_min, max=bill_max,
                    value=[bill_min, bill_max],
                    marks={int(bill_min): f"${int(bill_min)}", int(bill_max): f"${int(bill_max)}"},
                    tooltip={"always_visible": False, "placement": "bottom"}
                ),
                html.Br(),
                html.Label("Food service"),
                dbc.Checklist(
                    id="time",
                    options=[{"label": i, "value": i} for i in ["Lunch", "Dinner"]],
                    value=["Lunch", "Dinner"],
                    inline=True
                ),
                html.Br(),
                dbc.Button("Reset filter", id="reset", color="secondary", outline=True, className="w-100")
            ], className="p-3 bg-light border rounded")
        ], width=3),

        # Contenido Principal
        dbc.Col([
            # Fila de Value Boxes
            dbc.Row([
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H5(html.I(className="fas fa-user me-2")),
                        html.H4("Total tippers"),
                        html.H2(id="total_tippers")
                    ])
                ], color="primary", outline=True), width=6),
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H5(html.I(className="fas fa-dollar-sign me-2")),
                        html.H4("Average bill"),
                        html.H2(id="average_bill")
                    ])
                ], color="success", outline=True), width=6),
            ], className="mb-3"),

            # Fila de Tabla y Gráfico
            dbc.Row([
                dbc.Col(dbc.Card([
                    dbc.CardHeader("Tips data"),
                    dbc.CardBody(html.Div(id="table_container"), style={"maxHeight": "400px", "overflowY": "auto"})
                ]), width=6),
                dbc.Col(dbc.Card([
                    dbc.CardHeader([
                        "Total bill vs tip",
                        dbc.Button(html.I(className="fas fa-ellipsis-v"), id="open_popover", color="link", size="sm", className="float-end"),
                        dbc.Popover([
                            dbc.PopoverHeader("Add a color variable"),
                            dbc.PopoverBody(
                                dbc.RadioItems(
                                    id="scatter_color",
                                    options=[{"label": i, "value": i} for i in ["none", "sex", "smoker", "day", "time"]],
                                    value="none",
                                    inline=True
                                )
                            )
                        ], target="open_popover", trigger="click", placement="top")
                    ]),
                    dbc.CardBody(dcc.Graph(id="scatterplot"))
                ]), width=6),
            ])
        ], width=9)
    ])
], fluid=True)

# Callbacks (Lógica)

@callback(
    Output("total_tippers", "children"),
    Output("average_bill", "children"),
    Output("table_container", "children"),
    Output("scatterplot", "figure"),
    Input("total_bill", "value"),
    Input("time", "value"),
    Input("scatter_color", "value")
)
def update_dashboard(bill_rng, time_val, color_val):
    # Filtrado (Equivalente a tips_data() reactivo)
    df = tips[
        (tips["total_bill"].between(bill_rng[0], bill_rng[1])) & 
        (tips["time"].isin(time_val))
    ]
    
    # Cálculos
    tippers = len(df)
    avg_bill = f"${df['total_bill'].mean():.2f}" if not df.empty else "N/A"
    
    # Tabla
    table = dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{"name": i, "id": i} for i in df.columns],
        page_size=10,
        style_table={'overflowX': 'auto'}
    )
    
    # Gráfico
    color_arg = None if color_val == "none" else color_val
    fig = px.scatter(df, x="total_bill", y="tip", color=color_arg, trendline="lowess")
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))

    return tippers, avg_bill, table, fig

# Callback para Reset
@callback(
    Output("total_bill", "value"),
    Output("time", "value"),
    Input("reset", "n_clicks"),
    prevent_initial_call=True
)
def reset_filters(n):
    return [bill_min, bill_max], ["Lunch", "Dinner"]

if __name__ == "__main__":
    app.run()