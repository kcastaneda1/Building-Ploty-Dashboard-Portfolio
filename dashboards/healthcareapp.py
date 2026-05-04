import pandas as pd
from dash.dependencies import Input, Output
from dash import Dash, dcc, html, dash_table
import plotly.graph_objects as go
import plotly.express as px
from datetime import timedelta
from load_data.load_healthcare_data import get_connection_health
from app import app


def create_healthcare_app(server):
    dash_app = Dash(
        __name__,
        server=server,
        url_base_pathname="/healthcare/"
    )
    def style_figure(fig):
          fig.update_layout(
               legend = dict(
                    orientation = 'h',
                    y=1.02,
                    x=0.5,
                    xanchor = 'center',
                    yanchor = 'bottom'
               ),
               margin = dict(t=80),
               autosize = True
          )
          return fig
    con = get_connection_health()
    
    df_init = con.execute(
     """ 
     SELECT DISTINCT Provider_ID,
               Insurance_Type,
               Patient_Gender,
               Claim_Submission_Date,
               Fraud_Category
     FROM healthcare_fraud_v
     """
     ).df()
    
    con.close()
    
    providers = df_init['Provider_ID'].unique()
    insurances = df_init['Insurance_Type'].unique()
    genders = df_init['Patient_Gender'].unique()
    frauds = df_init['Fraud_Category'].unique()
    min_date = df_init['Claim_Submission_Date'].min()
    max_date = df_init['Claim_Submission_Date'].max()
    dash_app.layout = html.Div([
         html.H1('HealthCare Dashboard',
               style={
                    'textAlign':'center',
                    'marginBottom':'30px',
                    'padding':'30px'
                    }),
     html.Div([
          dcc.Dropdown(
               id = 'provider-dropdown',
               options = [{'label': f'{p}', 'value':p} for p in providers],
               multi = True, 
               value = providers
               ),
          dcc.Dropdown(
               id = 'insurance-dropdown', 
               options = [{'label': f'{i}','value':i} for i in insurances],
               value = insurances,
               multi = True
               ),
          dcc.DatePickerRange(
               id = 'date-range',
               min_date_allowed= min_date,
               max_date_allowed= max_date,
               start_date = min_date,
               end_date = max_date
               ),
          dcc.Dropdown(
               id = 'gender-dropdown',
               options = [{'label': f'{g}', 'value':g} for g in genders],
               value = genders,
               multi = True
               ),
          dcc.Dropdown(
               id = 'fraud-dropdown',
               options = [{'label':f'{f}', 'value':f} for f in frauds],
               value = frauds,
               multi = True
               )
     ], style={
          "display":'flex',
          "gap":'20px',
          "alignItems":'center',
          "justifyContent":'center',
          'marginBottom':'30px'
     }),
     html.Div([
          html.Div(id='kpi-total-claim-amount'),
          html.Div(id='kpi-total-approved-amount'),
          html.Div(id = 'kpi-avg-los')
     ], style={
          'display': 'flex',
          'justifyContent':'center',
          'gap':'20px',
          'marginBottom': '30px',
          'maxWidth':'1200px',
          'marginLeft':'auto',
          'marginRight':'auto',
          "flexWrap":'wrap' 
     }),
     html.Div([
          dcc.Graph('line-chart-health',
               style={'width':'100%', 'height':'40vh', "flex":'1 1 500px', 'minwidth':'300px'},
               config = {'responsive':True})
     ]),
     html.Div([
          dcc.Graph(
               id = 'insurance-bar',
               style = {"flex":'1', "minwidth":0},
               config={'responsive':True}
               ),
          dcc.Graph(
               id = 'provider-bar',
               style ={'flex':'1', 'minwidth':0},
               config={'responsive':True}
               ),
     ], style = {
          'display':'flex',
          "gap":'20px',
          "marginBottom":'30px',
          "width":'100%',
          'height':'40vh',
          "flexWrap":'wrap'
     }),
     html.Div([
          dcc.Graph(id = 'visit-pie',
                    style = {"flex":'1', "minwidth":0},
                    config={'responsive':True}
                    ),
          dcc.Graph(id='state-map',
                    style = {"flex":'1', "minwidth":0},
                    config={'responsive':True}
                    )
     ], style = {
          'display':'flex',
          "gap":'10px',
          "marginBottom":'30px',
          "width":'100%',
          "height":'40vh',
          "flexWrap":'wrap'
     })
     #dash_table.DataTable(id='summary-table')
     ])
    
    @dash_app.callback(
     Output('kpi-total-claim-amount', 'children'),
     Output('kpi-total-approved-amount', 'children'),
     Output('kpi-avg-los', 'children'),
     Output('line-chart-health','figure'),
     Output('insurance-bar','figure'),
     Output('provider-bar','figure'),
     Output('visit-pie','figure'),
     Output('state-map', 'figure'),
     Input('provider-dropdown','value'),
     Input('insurance-dropdown', 'value'),
     Input('date-range','start_date'),
     Input('date-range', 'end_date'),
     Input('gender-dropdown','value'),
     Input('fraud-dropdown', 'value')
     )
    
    def update_healthcare_graph(providers, insurances, start_date, end_date, genders, frauds):
     con = get_connection_health() 
     query = """
               SELECT * 
               FROM healthcare_fraud_v
               WHERE 1=1
               """
     params = []

     if providers:
               if isinstance(providers,str):
                    providers = [providers]
               query += f" AND Provider_ID IN ({','.join(['?'] * len(providers))})"
               params.extend(providers)     

     if insurances:
          query += f" AND Insurance_Type IN ({','.join(['?'] * len(insurances))})"
          params.extend(insurances)

     if genders:
          query += f" AND Patient_Gender IN ({','.join(['?'] * len(genders))})"
          params.extend(genders)

     if frauds:
          query += f" AND Fraud_Category IN ({','.join(['?'] * len(frauds))})"
          params.extend(frauds)    

     if start_date and end_date:
          query += " AND Claim_Submission_Date BETWEEN ? and ?"
          params.extend([start_date, end_date])

     print(query)
     print("Total placeholders:", query.count("?"))
     print("Total params:", len(params))

     df = con.execute(query, params).df()
     
     con.close()

     if df.empty:
          empty_fig = px.line(title="No Data")
          return "", "", "", empty_fig, empty_fig, empty_fig, empty_fig, empty_fig

     # KPIs
     total_claims_amount = df['Claim_Amount'].sum()
     total_approved_amount = df['Approved_Amount'].sum()
     avg_los = df['Length_of_Stay'].mean()

     # line chart
     df_grouped = df.groupby(['Claim_Submission_Date'])[['Claim_Amount','Approved_Amount']].sum().reset_index()
     line_fig = px.line(df_grouped, x = 'Claim_Submission_Date', y = ['Approved_Amount','Claim_Amount']) 

     # insurance type bar +  provider specialty bar
     insurance_df = df.groupby(['Insurance_Type'])[['Claim_Amount','Approved_Amount']].sum().reset_index()
     insurance_bar = px.bar(insurance_df, x = 'Insurance_Type', y = ['Claim_Amount', 'Approved_Amount'], opacity=0.9, orientation='v', barmode = 'group')
     provider_df = df.groupby(['Provider_Specialty'])[['Claim_Amount','Approved_Amount']].sum().reset_index()
     provider_bar = px.bar(provider_df, x = 'Provider_Specialty', y = ['Claim_Amount', 'Approved_Amount'], opacity=0.9, orientation='v', barmode = 'group')

     #pie 
     visit_df = df.groupby(['Visit_Type'])['Provider_ID'].count().reset_index()
     visit_pie = px.pie(visit_df, names='Visit_Type', values = 'Provider_ID')

     # map
     mapped_grouped = df.groupby(['Patient_State'])['Approved_Amount'].sum().reset_index()
     approved_mapped = px.choropleth(mapped_grouped, locations= 'Patient_State', locationmode='USA-states', scope='usa', color ='Approved_Amount')

     
     return(
               html.Div([html.P("Total Claim Amount"),html.H2(f"${total_claims_amount:,.0f}")]),
               html.Div([html.P("Total Approved Amount"), html.H2(f"${total_approved_amount:,.0f}")]),
               html.Div([html.P("Avg Los"), html.H2(f"{avg_los:,.2f}")]),
               style_figure(line_fig), 
               style_figure(insurance_bar), 
               style_figure(provider_bar), 
               style_figure(visit_pie), 
               style_figure(approved_mapped)
               )
    return dash_app
