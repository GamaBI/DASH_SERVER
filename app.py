from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from secciones.login import crear_layout_login, login_callback

# Crear la app
app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Dashboard Seguridad"

callbacks_registrados = {'dashboard': False}

# Layout principal
app.layout = lambda: html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='session-store'),
    html.Div(id='page-content')
])

# Callback para manejar el contenido según la URL 
# Este debe ser el primer callback que afecta a url.pathname
@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def cambiar_pagina(pathname):
    if pathname == '/dashboard':
        from secciones.dashboard import crear_dashboard, register_dashboard_callbacks
        if not callbacks_registrados['dashboard']:
            register_dashboard_callbacks(app)
            callbacks_registrados['dashboard'] = True
        return crear_dashboard()
    else:
        return crear_layout_login()

# Registrar el callback de login
login_callback(app)

if __name__ == '__main__':
    app.run(debug=True, host='192.168.223.188', port=8050)