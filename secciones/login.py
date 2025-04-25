from dash import html, dcc, Input, Output, State, callback_context
import dash
import dash_bootstrap_components as dbc

# Layout de Login
def crear_layout_login():
    return html.Div(
        className="split-screen-container",
        children=[
            html.Div(className="left-image"),
            html.Div(
                className="right-login",
                children=[
                    html.Div(
                        className="login-container",
                        children=[
                            html.H2("SUBGERENCIA DE SEGURIDAD CIUDADANA", className="titulo"),
                            html.H4("Municipalidad de San Isidro", className="subtitulo"),
                            dbc.InputGroup([
                                dbc.InputGroupText("🚹"),
                                dbc.Input(id="username", placeholder="Usuario", type="text", className="input-login"),
                            ]),
                            dbc.InputGroup([
                                dbc.InputGroupText("🔒"),
                                dbc.Input(id="password", placeholder="Contraseña", type="password", className="input-login"),
                            ]),
                            dbc.Button("Iniciar sesión", id="login-button", className="btn-login"),
                            
                            # Alerta para credenciales incorrectas
                            dbc.Alert(
                                "Usuario o contraseña incorrectos. Inténtelo nuevamente.",
                                id="login-error",
                                color="danger",
                                is_open=False,
                                dismissable=True,
                                className="mt-3"
                            ),
                            
                            # Alerta para login exitoso
                            dbc.Alert(
                                "¡Inicio de sesión exitoso! Redirigiendo...",
                                id="login-success-alert",
                                color="success",
                                is_open=False,
                                dismissable=True,
                                className="mt-3"
                            ),
                            
                            # Temporizador para redirección
                            dcc.Interval(id="redirect-timer", interval=1500, n_intervals=0, disabled=True),
                            
                            # Mantenemos el confirm dialog para compatibilidad
                            dcc.ConfirmDialog(id="login-alert", displayed=False),
                            dcc.Store(id="login-success", data=False),
                            dcc.Store(id="should-redirect", data=False)
                        ]
                    )
                ]
            )
        ]
    )

# Callback para login
def login_callback(app):
    # Primer callback: Valida credenciales y muestra mensajes
    @app.callback(
        [Output('login-error', 'is_open'),
         Output('login-success-alert', 'is_open'),
         Output('redirect-timer', 'disabled'),
         Output('session-store', 'data'),
         Output('should-redirect', 'data'),
         Output('login-alert', 'displayed')],  # Mantener para compatibilidad
        [Input('login-button', 'n_clicks')],
        [State('username', 'value'),
         State('password', 'value')],
        prevent_initial_call=True
    )
    def validar_login(n_login, username, password):
        if not n_login:
            return False, False, True, dash.no_update, False, False
            
        if username == 'admin' and password == 'admin':
            # Login exitoso - mostrar mensaje y habilitar temporizador
            return False, True, False, {'user': 'admin'}, True, False
        else:
            # Login fallido - mostrar mensaje de error
            return True, False, True, dash.no_update, False, False
    
    # Segundo callback: Redirecciona después del temporizador
    @app.callback(
        Output('url', 'pathname'),
        [Input('redirect-timer', 'n_intervals')],
        [State('should-redirect', 'data')],
        prevent_initial_call=True
    )
    def redirigir_despues_de_mensaje(n_intervals, should_redirect):
        if n_intervals > 0 and should_redirect:
            return '/dashboard'
        return dash.no_update