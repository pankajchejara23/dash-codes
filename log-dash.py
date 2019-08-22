import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
from collections import Counter
import dash_bootstrap_components as dbc
import pandas as pd
import io
import sys
from etherLogAnalyzer import etherLogAnalyzer

import plotly.graph_objs as go

app = dash.Dash(__name__,external_stylesheets=["/assets/bootstrap.css","/assets/plot.css"])
file_name = ""

error_flag = False
if len(sys.argv)!=2:

    print('Error: You have not specified the file name')
    print("Usage: python log_analyzer.py csv-file-name")
    sys.exit()
else:
    file_name = sys.argv[1]

analyzer = etherLogAnalyzer(file_name)


author_ips = analyzer.getAuthorIP()
user_df = {}
figure_data_add=[]
figure_data_del=[]
final_df = analyzer.generateWindowWiseStats()

print(final_df)

for i in range(len(author_ips)):
    if i >3:
        continue
    user_add='u%d_add'%(i+1)
    user_del='u%d_del'%(i+1)
    figure_data_add.append({'x':final_df['timestamp'],'y':final_df[user_add],'type':'bar','name':author_ips[i]})
    figure_data_del.append({'x':final_df['timestamp'],'y':final_df[user_del],'type':'bar','name':author_ips[i]})







table_header = [
    html.Thead(html.Tr([html.Th("Attribute"), html.Th("Value")]))
]

row1 = html.Tr([html.Td("No. of Participants"), html.Td(analyzer.getAuthorCount())])
row2 = html.Tr([html.Td("IPs"), html.Td('  '.join(analyzer.getAuthorIP()))])
row3 = html.Tr([html.Td("Duration:"), html.Td(analyzer.getDuration())])


table_body = [html.Tbody([row1, row2, row3])]


body = dbc.Container(
    [   dbc.Row([
            dbc.Col([
                html.H1("Etherpad Log Analyzer"),
                html.P("This web-app offers visualization of Log files collected from  Etherpad tool"+
                ". To track the activity of Etherpad users, we have developed a plugin (ep_update_trak)."+
                "This plugin records activity related data e.g. the ip-address, action-type, number of characters added or deleted, etc."),
                html.P("Tallinn University")


            ])
        ]),
        html.H3("Log Summary"),
        dbc.Table(html.Thead([html.Tbody([row1, row2, row3])])),

        html.Hr(),
        dbc.Row([
            dbc.Col([
                html.H3("Writing activity"),
                dcc.Graph(id='log_graph_add',
                figure={
                    'data':figure_data_add,
                    'layout':go.Layout(
                        xaxis={'title': 'Timestamp'},
                        yaxis={'title': 'No. of characters added'},
                        margin={'l': 40, 'b': 40, 't': 10, 'r': 40},
                    )

                }),
            ],md=7),
            dbc.Col([
                html.H3("Updating activity"),
                dcc.Graph(id='log_graph_del',
                figure={
                    'data':figure_data_del,
                    'layout':go.Layout(
                        xaxis={'title': 'Timestamp'},
                        yaxis={'title': 'No. of characters deleted'},
                        margin={'l': 40, 'b': 40, 't': 10, 'r': 40},
                    )

                })
            ],md=5)
        ]),
        html.Div(style={'padding': 40}),

        dbc.Row([
            dbc.Col([
                dcc.Slider(
                id='window',
                min=0,
                max=10,
                step=None,
                marks = {
                    0 : '30Sec',
                    1 : '60Sec',
                    2 : '2Min',
                    3 : '5Min',
                    4 : '15Min',
                    5 : '30Min',
                    6 : '60Min',
                    7 : '2Hr'
                },
                value = 0

                )
            ],md=12)

        ])

    ])


app.layout = html.Div([body])
@app.callback(Output('log_graph_add', 'figure'),
              [Input('window', 'value')])
def display_value(value):
    time_window={0:'30S',1:'60S',2:'2T',3:'5T',4:'15T',5:'30T',6:'60T',7:'120T'}
    figure_data=[]
    final_df = analyzer.generateWindowWiseStats(window_size=time_window[value])
    for i in range(len(author_ips)):
        if i >3:
            continue
        user_add='u%d_add'%(i+1)
        figure_data.append({'x':final_df['timestamp'],'y':final_df[user_add],'type':'bar','name':author_ips[i]})
    figure={
        'data':figure_data,
        'layout':go.Layout(
            xaxis={'title': 'Timestamp'},
            yaxis={'title': 'No. of characters added'},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 40},
        )

    }
    return figure


@app.callback(Output('log_graph_del', 'figure'),
              [Input('window', 'value')])
def display_value(value):
    time_window={0:'30S',1:'60S',2:'2T',3:'5T',4:'15T',5:'30T',6:'60T',7:'120T'}
    figure_data=[]
    final_df = analyzer.generateWindowWiseStats(window_size=time_window[value])
    for i in range(len(author_ips)):
        if i >3:
            continue

        user_del='u%d_del'%(i+1)
        figure_data.append({'x':final_df['timestamp'],'y':final_df[user_del],'type':'bar','name':author_ips[i]})
    figure={
        'data':figure_data,
        'layout':go.Layout(
            xaxis={'title': 'Timestamp'},
            yaxis={'title': 'No. of characters deleted'},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 40},
        )

    }
    return figure



if __name__ == '__main__':
    app.run_server(debug=True)
