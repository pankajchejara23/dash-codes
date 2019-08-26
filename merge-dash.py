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


import plotly.graph_objs as go

app = dash.Dash(__name__,external_stylesheets=["/assets/bootstrap.css","/assets/plot.css"])
file_name = ""

error_flag = False
"""
if len(sys.argv)!=3:

    print('Error: You have not specified two file names')
    print("Usage: python log_analyzer.py speech-csv-file log-csv-file")
    sys.exit()
else:
    log_name = sys.argv[1]
    speech_name = sys.argv[2]

"""




body = dbc.Container(
    [   dbc.Row([
            dbc.Col([
                html.H1("Merger Speech and Log Data"),
                html.P("This web app will allow you to merge audio and log data and download the merged data file."),
                html.P("Tallinn University")

            ])
        ]),
        dbc.Row([
            dbc.Label('Enter IP addresses'),
            dbc.Input(
            id="user-1",
            type="text",
            placeholder="Ip address of User-1",
            ),
            dbc.Input(
            id="user-2",
            type="text",
            placeholder="Ip address of User-2",
            ),
            dbc.Input(
            id="user-3",
            type="text",
            placeholder="Ip address of User-3",
            ),
            dbc.Input(
            id="user-4",
            type="text",
            placeholder="Ip address of User-4",
            ),
            dbc.Button("Merge Files", id="merge-button", color="primary", className="mr-2"),
        ]),
        html.Div([

            html.Span(id="example-output")
        ])


    ])


app.layout = html.Div([body])
@app.callback(
    Output("example-output", "children"), [Input("merge-button", "n_clicks"),Input("user-1","value"),Input("user-2","value"),Input("user-3","value"),Input("user-4","value")]
)
def on_button_click(n,v1,v2,v3,v4):
    if n is None:
        return "Not clicked."
    else:
        return f"Clicked {n} times."


if __name__ == '__main__':
    app.run_server(debug=True)
