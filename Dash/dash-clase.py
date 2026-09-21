from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np

# ==============================================================================
# 1. Carga y Preparación de los Datos
# ==============================================================================
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

# Traducción y limpieza
df = df.rename(columns={
    'country': 'pais',
    'continent': 'continente',
    'year': 'anio',
    'lifeExp': 'esperanza_vida',
    'pop': 'poblacion',
    'gdpPercap': 'pib_per_capita'
})

mapa_continentes = {
    'Asia': 'Asia', 'Europe': 'Europa', 'Africa': 'África', 
    'Americas': 'América', 'Oceania': 'Oceanía', 'FSU': 'Ex Unión Soviética'
}
df['continente'] = df['continente'].map(mapa_continentes).fillna(df['continente'])
df = df.dropna(subset=['pais', 'anio', 'esperanza_vida', 'pib_per_capita'])

# ==============================================================================
# 2. Configuración de la App y Diseño
# ==============================================================================
app = Dash(__name__, external_stylesheets=[
    dbc.themes.FLATLY, 
    "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap",
    "https://use.fontawesome.com/releases/v5.15.4/css/all.css"
])

PALETA = {
    "primario": "#2563EB",    # Azul principal
    "secundario": "#64748B",  # Gris pizarra
    "acento": "#F59E0B",      # Naranja para el país seleccionado
    "fondo": "#F8FAFC"        # Fondo general
}

estilo_tarjeta = {
    "border": "1px solid #E2E8F0", 
    "borderRadius": "12px", 
    "backgroundColor": "white",
    "marginBottom": "1.5rem",
    "boxShadow": "none"
}

# ==============================================================================
# 3. Interfaz de Usuario (UI)
# ==============================================================================
app.layout = dbc.Container([
    # -- ENCABEZADO --
    dbc.Row([
        dbc.Col([
            html.H2("Tablero de Desarrollo Global", className="mt-4 mb-2 fw-bold", style={"color": "#1E293B"}),
            html.P(
                "Este tablero analiza la evolución del desarrollo de los países mediante indicadores de "
                "población, esperanza de vida y PIB per cápita. Selecciona un continente, un país y un "
                "rango de años para comparar sus resultados con los promedios regionales y observar sus tendencias.",
                className="text-muted mb-4",
                style={"maxWidth": "900px", "fontSize": "1rem", "lineHeight": "1.6"}
            )
        ], width=12)
    ]),

    # -- PANEL DE FILTROS --
    dbc.Row([
        dbc.Col(
            dbc.Card(dbc.CardBody([
                html.H6([html.I(className="fas fa-sliders-h me-2"), "Parámetros de Análisis"], className="fw-bold text-primary mb-3"),
                dbc.Row([
                    dbc.Col([
                        html.Label("Macro-Región (Continente):", className="small text-muted fw-bold"),
                        dcc.Dropdown(
                            id='filtro-continente',
                            options=[{'label': c, 'value': c} for c in sorted(df['continente'].unique())],
                            value='América',
                            clearable=False
                        )
                    ], md=4),
                    dbc.Col([
                        html.Label("Nación Objetivo:", className="small text-muted fw-bold"),
                        dcc.Dropdown(id='filtro-pais', clearable=False)
                    ], md=4),
                    dbc.Col([
                        html.Label("Ventana de Observación (Años):", className="small text-muted fw-bold"),
                        dcc.RangeSlider(
                            id='filtro-anios',
                            min=df['anio'].min(),
                            max=df['anio'].max(),
                            step=1,
                            marks={int(year): str(year) for year in range(1950, 2011, 10)},
                            value=[1970, 2007],
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], md=4)
                ])
            ]), style=estilo_tarjeta), width=12
        )
    ]),

    # -- KPIs --
    dbc.Row(id='tarjetas-kpis', className="mb-4"),

    # -- SECCIÓN 1: PANORAMA GEOGRÁFICO Y COMPARATIVO --
    html.H5("I. Panorama Geográfico y Comparativo", className="fw-bold mb-3", style={"color": "#334155"}),
    dbc.Row([
        dbc.Col(
            dbc.RadioItems(
                id="selector-metrica-seccion1",
                options=[
                    {"label": "PIB per cápita", "value": "pib_per_capita"},
                    {"label": "Esperanza de Vida", "value": "esperanza_vida"}
                ],
                value="pib_per_capita", inline=True, className="mb-3 small fw-bold"
            ), width=12
        )
    ]),
    
    dbc.Row([
        # Gráfico 1: Mapa Coroplético (Reemplazo de las burbujas)
        dbc.Col(dbc.Card([
            dbc.CardHeader("Distribución Continental", className="bg-white fw-bold border-0 pt-4"),
            dbc.CardBody([
                html.P("Mapa de calor que muestra la intensidad de la métrica en la región durante el año más reciente.", className="text-muted small mb-0"),
                dcc.Graph(id='grafico-mapa', config={'displayModeBar': False})
            ])
        ], style=estilo_tarjeta), md=7),

        # Gráfico 2: Comparativa de Barras
        dbc.Col(dbc.Card([
            dbc.CardHeader("Desempeño frente a Promedios", className="bg-white fw-bold border-0 pt-4"),
            dbc.CardBody([
                html.P("Contraste directo del país seleccionado contra el promedio de su continente y el promedio global.", className="text-muted small mb-3"),
                dcc.Graph(id='grafico-comparativo-barras', config={'displayModeBar': False})
            ])
        ], style=estilo_tarjeta), md=5),
    ]),

    # -- SECCIÓN 2: TENDENCIAS Y LIDERAZGO --
    html.H5("II. Evolución Histórica y Liderazgo Regional", className="fw-bold mb-3 mt-2", style={"color": "#334155"}),
    dbc.Row([
        dbc.Col(
            dbc.RadioItems(
                id="selector-metrica-seccion2",
                options=[
                    {"label": "PIB per cápita", "value": "pib_per_capita"},
                    {"label": "Esperanza de Vida", "value": "esperanza_vida"}
                ],
                value="esperanza_vida", inline=True, className="mb-3 small fw-bold"
            ), width=12
        )
    ]),

    dbc.Row([
        # Gráfico 3: Tendencia Simple
        dbc.Col(dbc.Card([
            dbc.CardHeader("Trayectoria en el Tiempo", className="bg-white fw-bold border-0 pt-4"),
            dbc.CardBody([
                html.P("Comportamiento histórico de la métrica analizada para el país objetivo.", className="text-muted small mb-3"),
                dcc.Graph(id='grafico-tendencia-limpio', config={'displayModeBar': False})
            ])
        ], style=estilo_tarjeta), md=7),

        # Gráfico 4: Top 10
        dbc.Col(dbc.Card([
            dbc.CardHeader(id="titulo-top10", className="bg-white fw-bold border-0 pt-4"),
            dbc.CardBody([
                html.P("Clasificación de los países con los indicadores más altos de la región.", className="text-muted small mb-3"),
                dcc.Graph(id='grafico-top10-limpio', config={'displayModeBar': False})
            ])
        ], style=estilo_tarjeta), md=5),
    ])

], fluid=True, style={"fontFamily": "'Inter', sans-serif", "backgroundColor": PALETA['fondo'], "minHeight": "100vh", "padding": "2rem"})


# ==============================================================================
# 4. Lógica (Callbacks)
# ==============================================================================
@callback(
    Output('filtro-pais', 'options'),
    Output('filtro-pais', 'value'),
    Input('filtro-continente', 'value')
)
def actualizar_paises(continente):
    paises = sorted(df[df['continente'] == continente]['pais'].unique())
    # Preselecciones inteligentes por continente
    preferencias = ['Colombia', 'Mexico', 'Spain', 'South Africa', 'Japan', 'Australia']
    pais_defecto = paises[0]
    for pref in preferencias:
        if pref in paises:
            pais_defecto = pref
            break
    return [{'label': p, 'value': p} for p in paises], pais_defecto

@callback(
    Output('tarjetas-kpis', 'children'),
    Output('grafico-mapa', 'figure'),
    Output('grafico-comparativo-barras', 'figure'),
    Output('grafico-tendencia-limpio', 'figure'),
    Output('grafico-top10-limpio', 'figure'),
    Output('titulo-top10', 'children'),
    Input('filtro-pais', 'value'),
    Input('filtro-continente', 'value'),
    Input('filtro-anios', 'value'),
    Input('selector-metrica-seccion1', 'value'),
    Input('selector-metrica-seccion2', 'value')
)
def actualizar_dashboard(pais, continente, rango_anios, metrica_s1, metrica_s2):
    if not pais: return [], {}, {}, {}, {}, ""

    anio_min, anio_max = rango_anios
    df_pais = df[(df['pais'] == pais) & (df['anio'] >= anio_min) & (df['anio'] <= anio_max)]
    df_cont_actual = df[(df['continente'] == continente) & (df['anio'] == anio_max)].copy()
    
    if df_pais.empty or df_cont_actual.empty: return [], {}, {}, {}, {}, ""

    # 1. KPIs SUPERIORES
    datos_fin = df_pais.iloc[-1]
    datos_inicio = df_pais.iloc[0]

    def crear_kpi(titulo, valor, previo, prefijo=""):
        delta = ((valor - previo) / previo) * 100 if previo != 0 else 0
        color = "#10B981" if delta >= 0 else "#EF4444"
        icono = "fa-arrow-up" if delta >= 0 else "fa-arrow-down"
        return dbc.Col(dbc.Card(dbc.CardBody([
            html.H6(titulo, className="text-muted small fw-bold text-uppercase"),
            html.H3(f"{prefijo}{valor:,.0f}".replace(',', '.'), className="fw-bold mb-1", style={"color": PALETA['primario']}),
            html.Span([html.I(className=f"fas {icono} me-1"), f"{delta:+.1f}% vs {anio_min}"], style={"color": color, "fontSize": "0.85rem", "fontWeight": "600"})
        ]), className="border-0 shadow-sm"), width=4)

    kpis = [
        crear_kpi(f"Población ({anio_max}) - habitantes", datos_fin['poblacion'], datos_inicio['poblacion']),
        crear_kpi(f"Esperanza de Vida ({anio_max}) - años", datos_fin['esperanza_vida'], datos_inicio['esperanza_vida']),
        crear_kpi(f"PIB Per Cápita ({anio_max}) - USD", datos_fin['pib_per_capita'], datos_inicio['pib_per_capita'], "$")
    ]

    # 2. MAPA GEOGRÁFICO (Reemplazo visual limpio de las burbujas)
    es_dinero = (metrica_s1 == 'pib_per_capita')
    escala_color = "Blues" if es_dinero else "Teal"
    nombre_metrica_s1 = "PIB per cápita" if es_dinero else "Esperanza de vida"
    unidad_metrica_s1 = "USD" if es_dinero else "años"
    
    fig_mapa = px.choropleth(
        df_cont_actual, 
        locations="pais", 
        locationmode="country names",
        color=metrica_s1,
        hover_name="pais",
        color_continuous_scale=escala_color,
        template="plotly_white"
    )
    # Magia de Plotly: Hace zoom automático para mostrar solo los países del continente filtrado
    fig_mapa.update_geos(fitbounds="locations", visible=False)
    fig_mapa.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        title=f"{nombre_metrica_s1} ({unidad_metrica_s1}) - {anio_max}",
        coloraxis_colorbar=dict(title=unidad_metrica_s1, thickness=10)
    )

    # 3. COMPARATIVA DE BARRAS DIRECTA (Simplificada)
    df_global_actual = df[df['anio'] == anio_max]
    
    df_comp = pd.DataFrame({
        'Entidad': [pais, f"Promedio {continente}", "Promedio Global"],
        'Valor': [datos_fin[metrica_s1], df_cont_actual[metrica_s1].mean(), df_global_actual[metrica_s1].mean()],
        'Color': [PALETA['primario'], PALETA['secundario'], "#CBD5E1"]
    })
    
    fig_comp = px.bar(
        df_comp, x='Entidad', y='Valor', 
        text_auto='$.2s' if es_dinero else '.1f',
        template="plotly_white"
    )
    fig_comp.update_traces(marker_color=df_comp['Color'], textposition="outside", width=0.5)
    fig_comp.update_layout(
        margin=dict(l=0, r=0, t=20, b=0),
        xaxis_title="Entidad",
        yaxis_title=f"{nombre_metrica_s1} ({unidad_metrica_s1})"
    )

    # 4. TENDENCIA HISTÓRICA (Línea)
    nombre_metrica_s2 = "PIB per cápita" if metrica_s2 == 'pib_per_capita' else "Esperanza de vida"
    unidad_metrica_s2 = "USD" if metrica_s2 == 'pib_per_capita' else "años"
    fig_trend = px.line(df_pais, x='anio', y=metrica_s2, markers=True, template="plotly_white")
    fig_trend.update_traces(line_color=PALETA['primario'], line_width=3, marker=dict(size=8, color=PALETA['acento']))
    fig_trend.update_layout(
        margin=dict(l=0, r=20, t=10, b=0),
        xaxis_title="Año",
        yaxis_title=f"{nombre_metrica_s2} ({unidad_metrica_s2})"
    )

    # 5. TOP 10 PAÍSES (Barras Horizontales)
    top_10 = df_cont_actual.nlargest(10, metrica_s2).sort_values(by=metrica_s2, ascending=True)
    # Resaltar en naranja si el país seleccionado está en el Top 10
    top_10['Color'] = np.where(top_10['pais'] == pais, PALETA['acento'], PALETA['primario'])
    
    fig_top = px.bar(
        top_10, x=metrica_s2, y="pais", orientation='h',
        text_auto='$.2s' if metrica_s2 == 'pib_per_capita' else '.1f', 
        template="plotly_white"
    )
    fig_top.update_traces(marker_color=top_10['Color'], textposition="outside")
    fig_top.update_layout(
        margin=dict(l=0, r=20, t=10, b=0),
        xaxis_title=f"{nombre_metrica_s2} ({unidad_metrica_s2})",
        yaxis_title="País",
        xaxis=dict(showticklabels=False)
    )
    
    titulo_top = f"Top 10 Países - {'PIB per cápita' if metrica_s2 == 'pib_per_capita' else 'Esperanza de Vida'}"

    return kpis, fig_mapa, fig_comp, fig_trend, fig_top, titulo_top

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8052)