import datetime as dt
import pandas as pd

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output


app = dash.Dash(__name__)
app.title = 'GENERIC: COVID-19'

populations = ['STUDENTS', 'STAFF']
conditions = ['ISOLATED', 'QUARANTINED', 'RECOVERED']

studs_dc_pk = 166
studs_k_1 = 497
studs_2_3 = 489
studs_int = 707
studs_jh = 499
studs_hs = 947
studs_alt = 26
total_staff = 460
total_studs = studs_dc_pk+studs_k_1+studs_2_3+studs_int+studs_jh+studs_hs+studs_alt

df = pd.read_csv('Generic_Covid_Data.csv', parse_dates=['Date'])

app.layout = html.Div([
    html.Div([
        html.Div([
            html.H1('GENERIC COVID-19 DASHBOARD', style={'color':'white', 'marginTop':'auto', 'marginBottom':'auto', 'textShadow':'2px 2px 4px #000000'}),
            html.Img(src='assets/grad_cap2.png')
        ], style={'display':'flex', 'marginRight':'auto', 'marginLeft':'auto', 'width':'50%'})
    ], className="jumbotron jumbotron-cj", style={'textAlign':'center', 'background':'#a1a1a1'}),
    html.Div([
        html.Div([
            html.P('POPULATION', className="radio-label"),
             dcc.RadioItems(
                id='pop_radio',
                options=[{'label': pop, 'value':pop} for pop in populations],
                value=populations[0],
                labelStyle={'display':'inline-block', 'margin-right':'10px'},
            )
        ], className="col-6", style={'display':'flex'})

    ], className="row"),
    html.Div([
        html.Div([
            dcc.Graph(id='affected_bar_chart')
        ], className="col-6"),
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.H5('STUDENTS ISOLATED'),
                        html.P(id='student_iso_card_data')
                    ], className="card-body card-body-centered")
                ], className="col-5 card"),
                html.Div([
                    html.Div([
                        html.H5('STAFF ISOLATED'),
                        html.P(id='staff_iso_card_data')
                    ], className="card-body card-body-centered")
                ], className="col-5 offset-1 card")
            ], className="row"),
            html.Div([
                html.Div([
                    html.Div([
                        html.H5('STUDENTS QUARANTINED'),
                        html.P(id='student_q_card_data')
                    ], className="card-body card-body-centered")
                ], className="col-5 card"),
                html.Div([
                    html.Div([
                        html.H5('STAFF QUARANTINED'),
                        html.P(id='staff_q_card_data')
                    ], className="card-body card-body-centered")
                ], className="col-5 offset-1 card")
            ], className="row mt-5"),

            html.Div([
                html.Div([
                    html.Div([
                        html.H5('STUDENTS RECOVERED'),
                        html.P(id='student_rec_card_data')
                    ], className="card-body card-body-centered")
                ], className="col-5 card"),
                html.Div([
                    html.Div([
                        html.H5('STAFF RECOVERED'),
                        html.P(id='staff_rec_card_data')
                    ], className="card-body card-body-centered")
                ], className="col-5 offset-1 card")
            ], className="row mt-5"),
            
        ], className="col-6"),
    ], className="row"),
    html.Div([
        html.Div([
            html.P('CONDITION', className='radio-label mt-1'),
            dcc.Dropdown(
                id='cond_dropdown',
                options=[{'label': cond, 'value': cond} for cond in conditions],
                value=conditions[0],
                style={'width':'200px'}
            )
        ], style={'display':'flex'}, className='col-6')
    ], className="row"),
    html.Div([
        html.Div([
            dcc.Graph(id="site_pie_chart")
        ], className="col-6"),
        html.Div([
            dcc.Graph(id='site_time_series_chart')
        ], className="col-6"),
    ], className="row"),
    html.Div(id='most_recent_data_div', style={'display':'none'})

], className="container-fluid mt-1")

def get_pop_prefix(picked_pop: str) -> str:
    return 'STAFF' if picked_pop == 'STAFF' else 'STUD'

def get_cond_suffix(picked_cond: str) -> str:
    if picked_cond == 'ISOLATED':
        return 'ISO'
    elif picked_cond == 'QUARANTINED':
        return 'Q'
    else:
        return 'REC'

def build_gross_week_df(pop_df: pd.DataFrame, picked_pop: str, pop_total: int, cond_suffix: str) -> pd.DataFrame:
    prefix = 'STAFF' if picked_pop == 'STAFF' else 'STUD'

    gross_week_df = pd.DataFrame(df[df['Cond Type'] == f'{prefix}_{cond_suffix}'].groupby('Date')['Value'].sum())
    gross_week_df['FracEnrollment'] = gross_week_df.apply(lambda x: x['Value']/pop_total, axis=1)
    gross_week_df.reset_index(inplace=True)

    return gross_week_df

def build_affected_bar_chart(pop_df: pd.DataFrame, picked_pop: str) -> go.Figure:
    pop_total = total_staff if picked_pop == 'STAFF' else total_studs
    
    q_week_df = build_gross_week_df(pop_df, picked_pop, pop_total, 'Q')
    iso_week_df = build_gross_week_df(pop_df, picked_pop, pop_total, 'ISO')
    rec_week_df = build_gross_week_df(pop_df, picked_pop, pop_total, 'REC')

    iso_cnts = []
    q_cnts = []
    rec_cnts = []

    dates = []

    for date in q_week_df['Date']:    
        dates.append(f"{date.month}/{date.day}/{date.year}")
        iso_cnts.append(iso_week_df[iso_week_df['Date'] == date]['Value'].iloc[0])
        q_cnts.append(q_week_df[q_week_df['Date'] == date]['Value'].iloc[0])
        rec_cnts.append(rec_week_df[rec_week_df['Date'] == date]['Value'].iloc[0])

    data = [
        go.Bar(name='ISOLATED', x=dates, y=iso_cnts),
        go.Bar(name='QUARANTINED', x=dates, y=q_cnts),
        go.Bar(name='RECOVERED', x=dates, y=rec_cnts)
    ]

    layout = dict(
        title=dict(
            text=f'TOTAL {picked_pop} AFFECTED',
            xanchor='center',
            yanchor='top',
            x=0.5,
            y=0.9
        ),
        barmode='stack',
        xaxis=dict(type='category')
    )

    return go.Figure(data=data, layout=layout)

def build_recent_pie_chart(pop_cond_df: pd.DataFrame, picked_pop: str, picked_cond: str) -> go.Figure:
    max_date = pop_cond_df['Date'].max()
    
    most_recent_df = pop_cond_df[pop_cond_df['Date'] == max_date].dropna()
    most_recent_df = most_recent_df[most_recent_df['Value'] > 0]
    total = str(most_recent_df['Value'].sum()).replace('.0','')

    data = [go.Pie(
        labels=most_recent_df['Location'],
        values=most_recent_df['Value'],
        hole=0.3
    )]

    layout=dict(
        title=dict(
            text=f"DISTRIBUTION BY QTY. {picked_pop} {picked_cond} - {max_date.month}/{max_date.day}/{max_date.year}",
            xanchor='center',
            yanchor='top',
            x=0.5,
            y=0.9
        )
    )
    
    return go.Figure(data=data, layout=layout)

def build_site_time_series_chart(pop_cond_df: pd.DataFrame, picked_pop: str, picked_cond: str) -> go.Figure:

    prefix = get_pop_prefix(picked_pop)
    suffix = get_cond_suffix(picked_cond)

    traces=[]
    for site in pop_cond_df['Location'].unique():
        site_df = pop_cond_df[(pop_cond_df['Location'] == site) & (pop_cond_df['Cond Type'] == f"{prefix}_{suffix}")]
        trace = go.Scatter(
            x = site_df['Date'],
            y = site_df['Value'],
            name = site
        )
        traces.append(trace)

    layout=dict(
        title=dict(
            text=f"{picked_cond} {picked_pop} BY BUILDING",
            xanchor='center',
            yanchor='top',
            x=0.5,
            y=0.9
        )
    )
    return go.Figure(data=traces, layout=layout)

def create_most_recent_view_df(most_recent_df: pd.DataFrame) -> pd.DataFrame:
    sites = ['DC/PK', 'K-1', '2-3', 'INT', 'JH', 'HS', 'Alt', 'Other']

    cond_types = ['STAFF_ISO', 'STUD_ISO', 'STAFF_Q', 'STUD_Q', 'STAFF_REC', 'STUD_REC']

    rows = []
    for cond_type in cond_types:
        row = {}
        row['CONDITION'] = cond_type
        cond_df = most_recent_df[most_recent_df['Cond Type'] == cond_type]
        for site in sites:
            row[site] = cond_df[cond_df['Location'] == site]['Value'].iloc[0]    
        rows.append(row)

    view_df = pd.DataFrame(rows)
    #TODO: Reorder columns & create total column

    return view_df




@app.callback(
    [Output('affected_bar_chart', 'figure'),
    Output('site_pie_chart', 'figure'),
    Output('site_time_series_chart', 'figure'),
    Output('most_recent_data_div', 'children')], 
    [Input('pop_radio', 'value'),
    Input('cond_dropdown', 'value'),]
)
def update_controls(picked_pop:str, picked_cond: str):
    pop_df = pd.DataFrame()
    if picked_pop == 'STAFF':
        pop_df = df[(df['Cond Type'] == 'STAFF_ISO') | (df['Cond Type'] == 'STAFF_Q') | (df['Cond Type'] == 'STAFF_REC')]
    else:
        pop_df = df[(df['Cond Type'] == 'STUD_ISO') | (df['Cond Type'] == 'STUD_Q') | (df['Cond Type'] == 'STUD_REC')]

    prefix = get_pop_prefix(picked_pop)
    suffix = get_cond_suffix(picked_cond)

    pop_cond_df = pop_df[pop_df['Cond Type'] == f"{prefix}_{suffix}"]

    bar_chart = build_affected_bar_chart(pop_df, picked_pop)
    pie_chart = build_recent_pie_chart(pop_cond_df, picked_pop, picked_cond)
    time_series_chart = build_site_time_series_chart(pop_cond_df, picked_pop, picked_cond)

    most_recent_df = df[df['Date'] == df['Date'].max()]


    return bar_chart, pie_chart, time_series_chart, most_recent_df.to_json()

@app.callback(
    [Output('student_iso_card_data', 'children'),
    Output('student_q_card_data', 'children'),
    Output('student_rec_card_data', 'children'),
    Output('staff_iso_card_data', 'children'),
    Output('staff_q_card_data', 'children'),
    Output('staff_rec_card_data', 'children')],
    [Input('most_recent_data_div', 'children')]
)
def update_most_recent_controls(most_recent_json: str):
    most_recent_df = pd.read_json(most_recent_json)

    stud_iso_cnt = most_recent_df[most_recent_df['Cond Type'] == 'STUD_ISO']['Value'].sum()
    stud_iso_percent = round((stud_iso_cnt/total_studs)*100, 1)
    stud_q_cnt = most_recent_df[most_recent_df['Cond Type'] == 'STUD_Q']['Value'].sum()
    stud_q_percent = round((stud_q_cnt/total_studs)*100, 1)
    stud_rec_cnt = most_recent_df[most_recent_df['Cond Type'] == 'STUD_REC']['Value'].sum()
    stud_rec_percent = round((stud_rec_cnt/total_studs)*100, 1)

    staff_iso_cnt = most_recent_df[most_recent_df['Cond Type'] == 'STAFF_ISO']['Value'].sum()
    staff_iso_percent = round((staff_iso_cnt/total_staff)*100, 1)
    staff_q_cnt = most_recent_df[most_recent_df['Cond Type'] == 'STAFF_Q']['Value'].sum()
    staff_q_percent = round((staff_q_cnt/total_staff)*100, 1)
    staff_rec_cnt = most_recent_df[most_recent_df['Cond Type'] == 'STAFF_REC']['Value'].sum()
    staff_rec_percent = round((staff_rec_cnt/total_staff)*100, 1)

    stud_iso = f" {str(stud_iso_cnt).replace('.0','')} - {stud_iso_percent}%" 
    stud_q = f" {str(stud_q_cnt).replace('.0','')} - {stud_q_percent}%" 
    stud_rec = f" {str(stud_rec_cnt).replace('.0','')} - {stud_rec_percent}%" 

    staff_iso = f" {str(staff_iso_cnt).replace('.0','')} - {staff_iso_percent}%" 
    staff_q = f" {str(staff_q_cnt).replace('.0','')} - {staff_q_percent}%" 
    staff_rec = f" {str(staff_rec_cnt).replace('.0','')} - {staff_rec_percent}%" 

    # view_df = create_most_recent_view_df(most_recent_df)

    return stud_iso, stud_q, stud_rec, staff_iso, staff_q, staff_rec




if __name__ == '__main__':
    app.run_server(debug=True)