import pandas as pd
from dash.dependencies import Input, Output
from dash import Dash, dcc, html, dash_table
import plotly.express as px
from datetime import timedelta
from load_data.data_loader import get_connection


def create_sales_app(server):
    app = Dash(
        __name__,
        server=server,
        url_base_pathname="/sales/"
    )

    KPI_STYLE = {
        "background": "linear-gradient(135deg, #1f2937, #111827)",
        "color": "white",
        "padding": "20px",
        "borderRadius": "12px",
        "width": "100%",
        "boxShadow": "0px 6px 16px rgba(0,0,0,0.3)",
        "textAlign": "left"
    }

    def style_figure(fig):
        fig.update_layout(
            plot_bgcolor="#020617",
            paper_bgcolor="#020617",
            font=dict(color="white"),
            margin=dict(l=40, r=40, t=50, b=40)
        )
        return fig

    con = get_connection()

    # -------------------------
    # INITIAL DATA (LIGHT QUERY)
    # -------------------------
    df_init = con.execute("""
        SELECT DISTINCT store_id, date
        FROM retail_sales
    """).df()

    stores = df_init['store_id'].unique()
    min_date = df_init['date'].min()
    max_date = df_init['date'].max()

    # -------------------------
    # LAYOUT
    # -------------------------
    app.layout = html.Div([
        html.H1('Retail Sales Dashboard',
                style={
                    'textAlign': "center",
                    'color': 'white',
                    'marginBottom': '30px',
                    'backgroundColor': '#020617',
                    'padding': '30px'
                }),

        html.Div([
            dcc.Dropdown(
                id='store-dropdown',
                options=[{'label': f"Store {s}", "value": s} for s in stores],
                multi=True,
                value=[stores[0]]
            ),
            dcc.Dropdown(id='item-dropdown', multi=True),
            dcc.DatePickerRange(
                id='date-range',
                min_date_allowed=min_date,
                max_date_allowed=max_date,
                start_date=min_date,
                end_date=max_date
            ),
            dcc.Dropdown(
                id='time-filter',
                options=[
                    {'label': "Last 30 Days", 'value': '30D'},
                    {'label': "Last 60 Days", 'value': '60D'},
                    {'label': "Last 90 Days", 'value': '90D'},
                    {'label': "Last Year", 'value': '1Y'},
                    {'label': "All", 'value': 'ALL'}
                ],
                value='ALL'
            )
        ], style={
            'display': 'flex', 
            'gap':'20px',
            'alignItems':'center',
            'justifyContent':'center',
            'marginBottom':'30px'
        }),

        html.Div([
            html.Div(id='kpi-total-sales'),
            html.Div(id='kpi-avg-sales'),
            html.Div(id='kpi-store-count'),
            html.Div(id='kpi-top-store'),
        ], style={
            'display': 'flex',
            'justifyContent':'center',
            'gap':'20px',
            'marginBottom': '30px',
            'maxWidth':'1200px',
            'marginLeft':'auto',
            'marginRight':'auto'
        }),

        dcc.Graph(
            id='line-chart',
            style ={
                'display':'flex',
                'marginBottom':'30px'
            }),

        html.Div([
            dcc.Graph(id='bar-chart'),
            dcc.Graph(id='pie-chart')
        ], style={
            'display': 'flex',
            'gap':'20px',
            'marginBottom':'30px'
            }),

        dcc.Graph(id='rolling-chart',
                  style = {
                      'marginBottom':'30px'
                  }),

       # dash_table.DataTable(
       #     id="summary-table",
       #     columns=[{"name": "col1", "id": "col1"}],
       #     data=[],)
    ])

    # -------------------------
    # ITEM DROPDOWN
    # -------------------------
    @app.callback(
        Output('item-dropdown', 'options'),
        Output('item-dropdown', 'value'),
        Input('store-dropdown', 'value')
    )
    def update_items(selected_store):

        if isinstance(selected_store, str):
            selected_store = [selected_store]

        df = con.execute("""
            SELECT DISTINCT item_id
            FROM retail_sales
            WHERE store_id = ANY(?)
        """, [selected_store]).df()

        items = df['item_id'].tolist()

        options = [{'label': f"Item {i}", 'value': i} for i in items]

        return options, items[:1]

    # -------------------------
    # MAIN CALLBACK
    # -------------------------
    @app.callback(
        Output('line-chart', 'figure'),
        Output('kpi-total-sales', 'children'),
        Output('kpi-avg-sales', 'children'),
        Output('kpi-store-count', 'children'),
        Output('kpi-top-store', 'children'),
        Output('bar-chart', 'figure'),
        Output('pie-chart', 'figure'),
        Output('rolling-chart', 'figure'),
        #Output('summary-table', 'data'),
        #Output('summary-table', 'columns'),
        Input('store-dropdown', 'value'),
        Input('item-dropdown', 'value'),
        Input('time-filter', 'value'),
        Input('date-range', 'start_date'),
        Input('date-range', 'end_date'),
    )
    def update_graph(stores, items, time_filter, start_date, end_date):

        if isinstance(stores, str):
            stores = [stores]

        query = """
            SELECT *
            FROM retail_sales_v
            WHERE store_id = ANY(?)
        """
        params = [stores]

        if items:
            query += " AND item_id = ANY(?)"
            params.append(items)

        if start_date and end_date:
            query += " AND date BETWEEN ? AND ?"
            params.extend([start_date, end_date])

        df = con.execute(query, params).df()

        if df.empty:
            empty_fig = px.line(title="No Data")
            return empty_fig, "", "", "", "", empty_fig, empty_fig, empty_fig, [], []

        # time filter
        if time_filter != "ALL":
            max_date = df['date'].max()
            if time_filter == '30D':
                start_date = max_date - timedelta(days=30)
            elif time_filter == '60D':
                start_date = max_date - timedelta(days=60)
            elif time_filter == '90D':
                start_date = max_date - timedelta(days=90)
            elif time_filter == '1Y':
                start_date = max_date - timedelta(days=365)

            df = df[df['date'] >= start_date]

        # KPIs
        total_sales = df['total_sales'].sum()
        avg_sales = df['total_sales'].mean()
        store_count = df['store_id'].nunique()
        top_store = df.groupby('store_id')['total_sales'].sum().idxmax()

        # line
        df_grouped = df.groupby(['date', 'store_id'])['total_sales'].sum().reset_index()
        line_fig = px.line(df_grouped, x='date', y='total_sales', color='store_id')

        # bar + pie
        bar_df = df.groupby('store_id')['total_sales'].sum().reset_index().nlargest(10, 'total_sales')
        bar_fig = px.bar(bar_df, x='store_id', y='total_sales')
        pie_fig = px.pie(bar_df, names='store_id', values='total_sales')

        # rolling
        df = df.sort_values('date')
        df['rolling_7'] = df.groupby('store_id')['total_sales'].transform(lambda x: x.rolling(7).mean())
        rolling_fig = px.line(df, x='date', y='rolling_7', color='store_id')

        # table
        #table_df = df.groupby('store_id')['total_sales'].agg(['sum', 'mean', 'max', 'min']).reset_index()
        #table_df['rank'] = table_df['sum'].rank(ascending=False)

        return (
            style_figure(line_fig),
            html.Div([html.P("Total Sales"), html.H2(f"${total_sales:,.0f}")], style=KPI_STYLE),
            html.Div([html.P("Avg Sales"), html.H2(f"${avg_sales:,.0f}")], style=KPI_STYLE),
            html.Div([html.P("Stores"), html.H2(store_count)], style=KPI_STYLE),
            html.Div([html.P("Top Store"), html.H2(top_store)], style=KPI_STYLE),
            style_figure(bar_fig),
            style_figure(pie_fig),
            style_figure(rolling_fig)
            #table_df.to_dict('records'),
            #[{"name": col, "id": col} for col in table_df.columns]
        )

    return app