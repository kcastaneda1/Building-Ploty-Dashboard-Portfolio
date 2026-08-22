import pandas as pd
from dash.dependencies import Input, Output
from dash import Dash, dcc, html, dash_table
import plotly.graph_objects as go
import plotly.express as px
from datetime import timedelta
import dash_ag_grid as dag
from queries.medicaid_queries import get_enrollment_trend, get_medicaid_raw, get_state_enrollment_growth, get_call_center_trend, get_operational_performance
from .components import navbar


def create_healthcare_app(server):
    dash_app = Dash(
        __name__,
        server=server,
        url_base_pathname="/healthcare/"
    )
    def style_figure(fig):
          fig.update_layout(
               plot_bgcolor = "#D9DDDC",
               paper_bgcolor = 'white',
               font=dict(color='black'),
               title=dict(
                    x=0.5,
                    xanchor = 'center',
                    y=0.95,
                    yanchor='top'
               ),
               legend=dict(
                    font=dict(color='black'),
                    title_font=dict(color='black'),
                    orientation ='h',
                    yanchor = 'bottom',
                    y = 0.20,
                    xanchor = 'center',
                    x = 0.5
               ),
               margin=dict(l=20, r=20, t=50, b=40),
               autosize = True
          )
          return fig
    
    global_dataset = get_medicaid_raw()
    states = global_dataset['state_name'].unique()
    min_date = global_dataset['reporting_date'].min()
    max_date = global_dataset['reporting_date'].max()

    dash_app.layout = html.Div([
         navbar(),

         html.H1('Centers for Medicare & Medicaid Services',
               style={
                    'textAlign':'center',
                    'marginBottom':'30px',
                    'padding':'30px'
                    }),
          html.Div([
               #Global filter component
               dcc.Dropdown(
                    id = 'state-filter',
                    options=[{
                         'label': f'{i}',
                         'value': i
                    } for i in states]
               ),
               dcc.DatePickerRange(
                    id = 'date-filter',
                    start_date= min_date,
                    end_date = max_date,
                    style={'width':'300px'}
                    ),
               ],
               style = {
                    'width':'100%',
                    'display':'flex',
                    'gap': '20px',
                    'alignItems':'center',
                    'justifyContent':'center',
                    'margin': '0 auto 30px auto',
               }
          ),
          dcc.Store(
               id = 'global-filters',
               storage_type='memory'
          ),
          dcc.Graph(id='enrollment-trendline'),
          dcc.Graph(id='growth-bar'),
          dcc.Graph(id='call-line'),
          html.Div([
               html.H3(
                    'Operational Summary',
                    style={'textAlign':'center','marginBottom':'10px'}
               ),
               html.Button(
                    'Downlaod CSV',
                    id = 'download-operational.csv',
                    n_clicks=0
               ),
               dag.AgGrid(
                    id='operational-table',
                    rowData=[],
                    columnDefs=[],
                    style={'height':'500px'},
               ),
          ]), 
    ])

    @dash_app.callback(
              Output('global-filters','data'),
              Input('state-filter','value'),
              Input('date-filter','start_date'),
              Input('date-filter', 'end_date')
    )
    
    def update_global_filters(state, start_date, end_date):
         return{
              'state':state,
              'start_date': start_date,
              'end_date': end_date
         }
    @dash_app.callback(
         Output('operational-table','exportDataCsv'),
         Input('download-operational-csv', 'n_clicks'),
         prevent_initial_table = True
    )

    def download_operational_table(n_clicks):
         return True

    @dash_app.callback(
         Output('enrollment-trendline', 'figure'),
         Output('growth-bar','figure'),
         Output('call-line','figure'),
         Output('operational-table', 'rowData'),
         Output('operational-table', 'columnDefs'),
         Input('global-filters', 'data')
    )

    def update_figures(filters):
          if filters is None:
               filters = {
                    'state': states.tolist(),
                    'start_date': min_date.isoformat(),
                    'end_date': max_date.isoformat(),
               }

          enrollment_df = get_enrollment_trend(filters)
          enrollment_df['reporting_date'] = pd.to_datetime(enrollment_df['reporting_date'])
          value_vars = [
               "total_medicaid_chip_enrollment",
               "total_medicaid_enrollment",
               "total_chip_enrollment"
          ]

          if 'state_name' is enrollment_df.columns:
               states_list = sorted(enrollment_df['state_name'].dropna().unique())
               default_metric = 'total_medicaid_chip_enrollment'
               traces = []
               for metric in value_vars:
                    for state in states_list:
                         df_s = enrollment_df[enrollment_df['state_name'] == state].sort_values('reporting_date')
                         traces.append(
                              go.Scatter(
                                   x=df_s['reporting_date'],
                                   y=df_s[metric],
                                   mode='lines+markers',
                                   name=state,
                                   legendgroup=state,
                                   visible={metric == default_metric},
                              )
                         )

               medicaid_enr_fig = go.Figure(data=traces)
               buttons = []
               for metric in value_vars:
                    vis = []
                    for current_metric in value_vars:
                         vis.extend([current_metric == metric] * len(states_list))
                    buttons.append(
                         dict(
                              label=metric,
                              method='update',
                              args=[
                                   {'visible': vis},
                                   {'title': f'<b>Medicaid and CHIP Enrollment Trend ({metric}</b>)'}
                              ]
                         )
                    )

               medicaid_enr_fig.update_layout(
                    updatemenus=[
                         dict(
                              active=value_vars.index(default_metric),
                              buttons=buttons,
                              direction='down',
                              x=0.0,
                              xanchor='left',
                              y=1.15,
                              yanchor='top'
                         )
                    ],
                    title={
                         'text': f"<b>Medicaid and CHIP Enrollment Trend ({default_metric}</b>)"
                    }
               )
          else:
               medicaid_enr_fig = px.line(
                    enrollment_df,
                    x='reporting_date',
                    y=value_vars,
                    markers=True,
                    labels={
                         'reporting_date': 'Reporting Date',
                         'value': 'Enrollment',
                         'variable': 'Program'
                    },
                    title='<b>Medicaid and CHIP Enrollment Trend</b>'
               )

          growth_df = get_state_enrollment_growth(filters)
          grw_fig = px.bar(
               growth_df,
               x="state_name",
               y="enrollment_change",
               labels={
                    "state_name": "State",
                    "enrollment_change": "Enrollment Change"
               },
               title='<b>State Medicaid & CHIP Enrollment Change</b>'
          )

          call_center_df = get_call_center_trend(filters)
          call_center_fig = px.line(
               call_center_df,
               x="reporting_date",
               y="total_call_volume",
               color="state_name",
               markers=True,
               labels={
                    "reporting_date": "Reporting Date",
                    "total_call_volume": "Call Volume"
               },
               title="<b>Call Center Volume Trend</b>"
          )

          operational_df = get_operational_performance(filters).fillna(0)
          column_defs = [
               {
                    "field": col,
                    "headerName": col.replace("_", " ").title(),
                    "sortable": True,
                    "filter": True,
               }
               for col in operational_df.columns
          ]

          return (
               style_figure(medicaid_enr_fig),
               style_figure(grw_fig),
               style_figure(call_center_fig),
               operational_df.to_dict("records"),
               column_defs,
          )
    return dash_app
