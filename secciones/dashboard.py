from dash import html, dcc, Input, Output, ctx, no_update
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

from secciones.exportar import exportar_a_excel, exportar_a_pdf

# Cargar datos
df = pd.read_excel("C:/Users/Gama/Desktop/DASH_SERVER/data/dataASI.xlsx")
df['FECCASO'] = pd.to_datetime(df['FECCASO'], errors='coerce')
df['Año'] = df['FECCASO'].dt.year
df['Mes'] = df['FECCASO'].dt.month
df['Día de la semana'] = df['FECCASO'].dt.day_name()
df['Hora'] = df['FECCASO'].dt.hour

# Funciones auxiliares
def color_semaforo(v, m): 
    return '#2ECC71' if v<=m*0.33 else '#F1C40F' if v<=m*0.66 else '#E74C3C'

def aplicar_estilo_barras(fig, data):
    m = data['Casos'].max()
    cols = [color_semaforo(v, m) for v in data['Casos']]
    fig.update_traces(
        marker_color=cols,
        text=data['Casos'],
        textposition='inside',
        insidetextanchor='middle'
    ).update_layout(
        uniformtext_minsize=10,
        uniformtext_mode='show',
        plot_bgcolor='#fefefe',
        font=dict(family='"Segoe UI", sans-serif', size=14, color='#2c3e50')
    )

# Layout del dashboard
def crear_dashboard():
    tipo_opts = [{'label': t,'value':t} for t in sorted(df['TXTTIPOCASO'].dropna().unique())]
    mes_opts  = [{'label': m,'value':m} for m in sorted(df['Mes'].dropna().unique())]

    return html.Div([
        dcc.Download(id="descarga"),
        html.H1(
            "👮‍ Dashboard de Seguridad Ciudadana - San Isidro",
            className="dashboard-title text-center mb-4 text-white p-3 rounded",
            style={'backgroundColor':'#655b17','fontFamily':'Impact,Charcoal,sans-serif'}
        ),

        dbc.Row([  # Filtros
            dbc.Col([dcc.Dropdown(id='filtro-tipo', options=tipo_opts, multi=True, placeholder="Filtrar por Tipo de Caso")], md=6),
            dbc.Col([dcc.Dropdown(id='filtro-mes', options=mes_opts, multi=True, placeholder="Filtrar por Mes")], md=6)
        ], className="mb-3"),

        dbc.Row([  # Total de casos
            dbc.Col(html.Div(id='total-casos', className="bg-light text-center p-4 shadow rounded border-warning mb-4"), width=12)
        ]),

        dbc.Row([  # Gráficos
            dbc.Col(dcc.Graph(id='grafico-ano'), width=12),
        ]),

        dbc.Row([  # Gráficos adicionales
            dbc.Col(dcc.Graph(id='grafico-dia'), md=6),
            dbc.Col(dcc.Graph(id='grafico-hora'), md=6)
        ]),

        dbc.Row([  # Gráfico por tipo
            dbc.Col(dcc.Graph(id='grafico-tipo'), md=6),
        ]),

        dbc.Row([  # Botones de exportación
            dbc.Col(dbc.Button("📄 Exportar a Excel", id="btn-export-excel", color="success", className="w-100"), md=6),
            dbc.Col(dbc.Button("🦾 Exportar a PDF",   id="btn-export-pdf", color="danger",  className="w-100"), md=6)
        ], className="mt-4"),

        dbc.Row([  # Cerrar sesión
            dbc.Col(dbc.Button("🔒 Cerrar Sesión", id="btn-cerrar-sesion", color="secondary", className="w-100 mt-4"))
        ]),

        # Toast de exportación
        dbc.Toast(
            "Archivo generado con éxito",
            id="toast-export",
            header="Operación completada",
            icon="success",
            is_open=False,
            dismissable=True,
            duration=3000,
            style={"position":"fixed","top":66,"right":10,"width":350}
        )
    ], className="p-5 rounded shadow-lg bg-white")

# Registrar los callbacks del dashboard
def register_dashboard_callbacks(app):
    @app.callback(
        [Output('grafico-ano','figure'),
         Output('grafico-dia','figure'),
         Output('grafico-hora','figure'),
         Output('grafico-tipo','figure'),
         Output('total-casos','children')],
        [Input('filtro-tipo','value'),
         Input('filtro-mes','value')]
    )
    def actualizar(filtro_tipo, filtro_mes):
        dff = df.copy()
        if filtro_tipo: dff = dff[dff['TXTTIPOCASO'].isin(filtro_tipo)]
        if filtro_mes:  dff = dff[dff['Mes'].isin(filtro_mes)]

        total = len(dff)
        df_ano = dff.groupby('Año').size().reset_index(name='Casos')
        df_dia = dff.groupby('Día de la semana').size().reset_index(name='Casos')
        df_hora= dff.groupby('Hora').size().reset_index(name='Casos')
        df_tipo= dff.groupby('TXTTIPOCASO').size().reset_index(name='Casos')

        fig_ano = px.bar(df_ano, x='Año', y='Casos', text='Casos', title='Casos por Año'); aplicar_estilo_barras(fig_ano,df_ano)
        fig_dia = px.bar(df_dia, x='Día de la semana', y='Casos', text='Casos', title='Casos por Día'); aplicar_estilo_barras(fig_dia,df_dia)
        fig_hora= px.bar(df_hora,x='Hora',             y='Casos', text='Casos', title='Casos por Hora'); aplicar_estilo_barras(fig_hora,df_hora)
        fig_tipo= px.bar(df_tipo,x='TXTTIPOCASO',      y='Casos', text='Casos', title='Casos por Tipo'); aplicar_estilo_barras(fig_tipo,df_tipo)

        return fig_ano,fig_dia,fig_hora,fig_tipo,f"Total de Casos: {total}"

    # Exportar a Excel o PDF
    @app.callback(
        [Output("descarga","data"),
         Output("toast-export","is_open")],
        [Input("btn-export-excel","n_clicks"),
         Input("btn-export-pdf","n_clicks")],
        prevent_initial_call=True
    )
    def exportar(excel_clicks, pdf_clicks):
        trigger = ctx.triggered_id
        if trigger=="btn-export-excel":
            path = exportar_a_excel(df)
            return dcc.send_file(path), True
        if trigger=="btn-export-pdf":
            path = exportar_a_pdf(df)
            return dcc.send_file(path), True
        return no_update, False

    # Cerrar sesión (No cambies el resto del archivo, solo este callback)
    @app.callback(
        Output('url', 'pathname', allow_duplicate=True),
        Input('btn-cerrar-sesion', 'n_clicks'),
        prevent_initial_call=True
    )
    def logout(n):
        if n:
            return '/'  # Nota: Usamos / en lugar de /login para ser consistentes
        return no_update