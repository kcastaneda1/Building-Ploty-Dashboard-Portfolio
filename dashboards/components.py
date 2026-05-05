from dash import html

def navbar():
    return html.Div([
        html.A("Home", href='/', style={'marginRight':"15px"}),
        html.A("Sales", href="/sales/", style={'marginRight':'15px'}),
        html.A('Healthcare', href='/healthcare/', style={'marginRight':'15px'}),
    ],
    style={
        'padding':'15px',
        'backgroundColor':"#f8f9fa",
        'borderBottom': '1px solid #ddd',
    },)