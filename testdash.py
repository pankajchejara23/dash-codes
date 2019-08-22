import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
from collections import Counter
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import networkx as nx
import base64
import io
import sys

from ReAudio import ReAudio

import plotly.graph_objs as go

def generateElements(edge_list,sp_time):

    total_sp = sum(sp_time.values())
    ele=[]
    G = nx.Graph()
    for edge in edge_list:

    # Check if the current edge already exist or not
        if G.has_edge(edge[0],edge[1]):

            # Get the weight of that edge
            w = G[edge[0]][edge[1]]['weight']

            # Remove it from the graph
            G.remove_edge(edge[0],edge[1])

            # Add it again with updated weight
            G.add_edge(edge[0],edge[1],weight=w+1)

        else:

            # If edge doesn't exist in the graph then add it with weight .5
            G.add_edge(edge[0],edge[1],weight=1)
    total_edges = len(edge_list)
    for n in list(G):
        user = 'User-'+str(n)
        speak_ratio = 200*sp_time[n]/total_sp
        t = {'id':n,'label':user,'width':speak_ratio}
        ele.append({'data':t})
    for e in G.edges:
        t = {'source':e[0],'target':e[1],'weight':G[e[0]][e[1]]['weight']*(30/total_edges)}
        ele.append({'data':t})

    return ele

app = dash.Dash(__name__,external_stylesheets=["bootstrap.css"])

# accessing file name from command line argument
file_name = sys.argv[1]

df = pd.read_csv('Tobias_meeting.CSV',names=['timestamp','direction'])

re = ReAudio('Tobias_meeting.CSV')
sp_time = re.getSpeakingTime(plot=False)

re.generateEdgeFile()
elements = generateElements(re.edge_list,sp_time)
print(elements)



dfreq = Counter(df['direction'])

directions=  df['direction'].unique()

freq = []
for dir in directions:
    c = df.loc[df['direction']==dir,:].shape[0]

    freq.append(c)

sp_user = [user for user in sp_time.keys()]
sp_duration = [sp for sp in sp_time.values()]

body = dbc.Container(
    [   dbc.Row([
            dbc.Col([
                html.H1("Log and Speech Analyzer"),
                html.P("This web-app offers visualization of Log files collected from ReSpeaker and Etherpad Usage"+
                ". It is developed using Python Dash Framework and utilizes Bootstrap for styling the page."),
                html.P("CEITER Team"),
                html.P("Tallinn University")


            ])
        ]),

        dcc.Upload(
            id='upload-data',
            children=html.Div([
                html.H4('Drag and Drop File '),
                html.A('or Select File')
            ]),
            style={
                'width': '98%',
                'height': '90px',
                'lineHeight': '60px',
                'borderWidth': '2px',
                'borderStyle': 'dashed',
                'borderRadius': '3px',
                'textAlign': 'center',
                'margin': '10px'
            }
        ),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                html.H2("Dataset Information"),
                html.P("")
            ],md=4),
            dbc.Col([
                html.H3("DoA (Direction of Arrival) Distribution"),
                dcc.Graph(id='doa')
            ],md=8)
        ]),
        dbc.Row([
            html.H3("Speaking Time")
        ]),
        dbc.Row([
            dbc.Col([
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
            ],md=5),
            dbc.Col([
                html.H3("How speaking time computed?"),
                html.P("First of all, DoA distribution is computed (shown in above figure). From the distribution, frequent occuring directions are retrieved. Then these directions are processed to filter out a direction if it is close to another direction. Out of these, four directions are then extracted and assigned to users in clockwise."),
                html.P("Additionally, it also assume that speaker does not move while speaking.")
            ])

        ]),
        dbc.Row([
            html.H3("Group Dynamics"),

        ]),
        dbc.Row([
            cyto.Cytoscape(
                id='cytoscape-layout-1',
                elements=elements,
                style={'width': '600%', 'height': '350px'},
                layout={
                    'name': 'circle'
                },
                stylesheet=[
                    {
                        'selector':'node',
                        'style':{
                            'label':'data(label)',
                            'width':'data(width)',
                            'height':'data(width)'

                        }
                    },
                    {
                        'selector': '[weight]',
                        'style':{
                            'width':'data(weight)'

                        }

                    }

                ]
            )

        ])
    ])

app.layout = html.Div([body])

def parse_data(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    print(decoded.decode('utf-8'))
    output = io.StringIO()
    output.write(decoded.decode('utf-8'))
    output.seek(0)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV or TXT file
            print('readind csv file----------')
            df = pd.read_csv(io.BytesIO(decoded))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        elif 'txt' or 'tsv' in filename:
            # Assume that the user upl, delimiter = r'\s+'oaded an excel file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), delimiter = r'\s+')
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return df


@app.callback(Output('doa', 'figure'),
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ])

def update_graph(contents, filename):
    print(contents)

    if contents:
        contents = contents
        filename = filename
        df = parse_data(contents, filename)
        df.columns=['timestamp','temp']
        df['direction'] = df['temp'].apply(lambda x:x.split(',')[1])
        print(df)
        print('Columns in df',df.columns)
        dfreq = Counter(df['direction'])

        directions=  df['direction'].unique()

        freq = []
        for dir in directions:
            c = df.loc[df['direction']==dir,:].shape[0]

            freq.append(c)

        df = df.set_index(df.columns[0])
        figure={
            'data':[
                {'x':directions,'y':freq,'type':'bar','name':'DoA distribution'}
            ],
            'layout':go.Layout(
                xaxis={'title': 'Updated Direction of Arrival'},
                yaxis={'title': 'Frequency'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 40},
            )
        }


        print(figure)
        return figure


if __name__ == '__main__':
    app.run_server(debug=True)
