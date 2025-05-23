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

user_selector=[]
time_scale=0
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

app = dash.Dash(__name__,external_stylesheets=["/assets/bootstrap.css","/assets/plot.css"])
file_name = ""

error_flag = False
if len(sys.argv)!=2:
    print('Error: You have not specified the file name')
    print("Usage: python dash-speech.py csv-file-name")
    sys.exit()
else:
    file_name = sys.argv[1]
    try:
        df = pd.read_csv(file_name,names=['timestamp','direction'])
    except Exception as e:
        print('Error:',str(e))
        sys.exit()

# Get speaking features and edge file
re = ReAudio(file_name)
sp_time = re.getSpeakingTime(plot=False)
re.generateEdgeFile()
elements = generateElements(re.edge_list,sp_time)

figure_data1=[]
final_df = re.generateWindowWiseSpeakingTime(window_size="30s")

# Prepared data for plotting
for i in range(4):
    user='u%d_speak'%(i+1)
    user_label = 'User-%d'%(i+1)
    figure_data1.append({'x':final_df['timestamp'],'y':final_df[user],'type':'bar','name':user_label})


dfreq = Counter(df['direction'])
directions=  df['direction'].unique()
freq = []
for dir in directions:
    c = df.loc[df['direction']==dir,:].shape[0]
    freq.append(c)
sp_user = [user for user in sp_time.keys()]
sp_duration = [sp for sp in sp_time.values()]


## HTML components
body = dbc.Container(
    [   dbc.Row([
            dbc.Col([
                html.H1("Speech Analyzer"),
                html.P("This web-app offers visualization of Log files collected from ReSpeaker and Etherpad Usage"+
                ". It is developed using Python Dash Framework and utilizes Bootstrap for styling the page."),
                html.P("Tallinn University")
            ])
        ]),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                html.H3("Direction of Arrival"),
                html.P("DoA (Direction of Arrival) represents the direction from which sound is detected by Raspberry prototype. DoA distribution (right figure) shows the freqeuncy of direction detected during recording. "),
                html.P("Voice activity detection (VAD) and Direction of Arrival (DoA) algorithms are used to detect voice and it's direction.")
            ],md=4),
            dbc.Col([
                html.H3("DoA  Distribution"),
                dcc.Graph(id='doa',
                figure={
                    'data':[
                        {'x':directions,'y':freq,'type':'bar','name':'DoA distribution'}
                    ],
                    'layout':go.Layout(
                        xaxis={'title': 'Direction of Arrival (In degree)'},
                        yaxis={'title': 'Frequency'},
                        margin={'l': 40, 'b': 40, 't': 10, 'r': 40},
                    )
                })
            ],md=8)
        ]),
        dbc.Row([
            html.H3("Speaking Time")
        ]),
        html.Hr(),
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
                html.H3("How speaking time is computed?"),
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

        ]),
        html.H3("Speaking behavior over time"),
        html.P("You can select the time duration within which you want explore the speaking behavior."),

        dbc.Row([
            dbc.Col([
                dcc.Checklist(id='user_selector',
                    options=[
                        {'label': 'User-1', 'value': 1},
                        {'label': 'User-2', 'value': 2},
                        {'label': 'User-3', 'value': 3},
                        {'label': 'User-4', 'value': 4}
                    ],
                    value=[1,2,3,4]
                )
                ],md=2),
            dbc.Col([
                dcc.Graph(id='speech_graph_time',
                figure={
                    'data':figure_data1,
                    'layout':go.Layout(
                        xaxis={'title': 'Timestamp'},
                        yaxis={'title': 'Speaking Time(Sec)'},
                        margin={'l': 40, 'b': 40, 't': 10, 'r': 40},
                    )
                })
                ],md=10)
        ]),
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
            ])
        ])
    ])

app.layout = html.Div([body])

## Event handling
@app.callback(Output('speech_graph_time', 'figure'),
              [Input('window', 'value'),Input('user_selector', 'value')])
def display_value(value,user_value):
    print(user_value)
    time_window={0:'30s',1:'60s',2:'2T',3:'5T',4:'15T',5:'30T',6:'60T',7:'120T'}
    figure_data=[]
    time = 'sec'
    if value > 0 and value < 6:
        time = 'min'
    elif value >5 :
        time = 'hour'
    final_df = re.generateWindowWiseSpeakingTime(window_size=time_window[value],time=time)
    for i in range(4):
        user='u%d_speak'%(i+1)
        user_label = 'User-%d'%(i+1)
        if (i+1) in user_value:
            figure_data.append({'x':final_df['timestamp'],'y':final_df[user],'type':'bar','name':user_label})
    figure={
        'data':figure_data,
        'layout':go.Layout(
            xaxis={'title': 'Timestamp'},
            yaxis={'title': 'Speaking Time ('+time+')'},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 40},
        )

    }
    return figure


if __name__ == '__main__':
    print('Running server')
    app.run(debug=False)
