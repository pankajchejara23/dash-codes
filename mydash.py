import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
from collections import Counter
import dash_bootstrap_components as dbc


from ReAudio import ReAudio

import plotly.graph_objs as go

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__,external_stylesheets=external_stylesheets)

df = pd.read_csv('Tobias_meeting.CSV',names=['timestamp','direction'])

re = ReAudio('Tobias_meeting.CSV')

sp_time = re.getSpeakingTime(plot=False)

dfreq = Counter(df['direction'])

directions=  df['direction'].unique()

freq = []
for dir in directions:
    c = df.loc[df['direction']==dir,:].shape[0]

    freq.append(c)

sp_user = [user for user in sp_time.keys()]
sp_duration = [sp for sp in sp_time.values()]


app.layout = html.Div([
    html.H1(children='Log and Speech Analyzer',style={
        'textAlign':'center'
    }),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            html.H3('Drag and Drop File '),
            html.A('Select Files')
        ]),
        style={
            'width': '98%',
            'height': '80px',
            'lineHeight': '60px',
            'borderWidth': '2px',
            'borderStyle': 'dashed',
            'borderRadius': '3px',
            'textAlign': 'center',
            'margin': '10px'
        }
    ),
    dcc.Graph(id='fig1',
    figure={
        'data':[
            {'x':directions,'y':freq,'type':'bar','name':'DoA distribution'}
        ],
        'layout':go.Layout(
            xaxis={'title': 'Direction of Arrival'},
            yaxis={'title': 'Frequency'},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 40},



        )

    }),
    html.H3('Speaking Time'),
    dcc.Graph(id='fig2',
    figure={
        'data':[
            {'x':sp_user,'y':sp_duration,'type':'bar','name':'Speaking Time'}
        ],
        'layout':go.Layout(
            xaxis={'title': 'User'},
            yaxis={'title': 'Speaking Time (sec.)'},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 40},



        )

    })
])


if __name__ == '__main__':
    app.run_server(debug=True)
