# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import pandas as pd

from plotly import graph_objs as go
from plotly.graph_objs import *
from dash.dependencies import Input, Output, State

# launch app with external css
external_stylesheets = ['https://codepen.io/kangbolu/pen/WNeWGyK.css']
app = dash.Dash(__name__,
                external_stylesheets=external_stylesheets)
app.title = 'NYC Wi-Fi Hotspots'

# API keys and datasets
mapbox_access_token = 'pk.eyJ1Ijoia2FuZ2JvbHUiLCJhIjoiY2p5ZTRhdHRvMHhqeDNpbzF5cm9kbjFhNyJ9.vydoqmQGx0UhJ7l23K_s0A'
map_data = pd.read_csv("nyc-wi-fi-hotspot-locations.csv")

# Selecting only required columns
map_data = map_data[["BoroName", "Type", "Provider", "Name", "SSID", "Location", "Location_T", "Latitude", "Longitude"]].drop_duplicates()

# count by block
Borough_counts = map_data["BoroName"].value_counts(sort=True)
Borough_counts_index = Borough_counts.index.tolist()

# layout for map
layout_map = dict(
    autosize=True,
    font=dict(color="#191A1A"),
    titlefont=dict(color="#191A1A", size='14'),
    margin=dict(
        l=20, r=20,  b=20, t=20
    ),
    hovermode="closest",
    plot_bgcolor='#fffcfc',
    paper_bgcolor='#fffcfc',
    legend=dict(font=dict(size=10), orientation='h'),
    title='WiFi Hotspots in NYC',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="light",
        center=dict(
            lon=-73.91251,
            lat=40.7342
        ),
        zoom=9.5,
    )
)

# # Function to generate scattermap
# def gen_map(map_data):
#     # groupby returns a dictionary mapping the values of the first field
#     # 'classification' onto a list of record dictionaries with that
#     # classification value.
#     return {
#         "data": data,
#         "layout": layout_map
#     }

# app layout
app.layout = html.Div(
    html.Div([
        html.Div(
            [
                html.H2(children='NYC WIFI Data',
                        className='nine columns'),
                html.Img(
                    src="https://www1.nyc.gov/assets/home/images/global/nyc.png",
                    className='three columns',
                    style={
                        'height': '9%',
                        'width': '9%',
                        'float': 'right',
                        'position': 'relative',
                        'paddingTop': 12,
                        'paddingRight': 0
                    },
                ),
                html.Div(children='''
                        Dash Visualization with map and various charts.
                        ''',
                        className='nine columns',
                        style={'marginLeft': 0}
                )
            ], 
            className="row"
        ),

        #---------------------------------------
        # ROW: 2 control components side by side
        #---------------------------------------
        html.Div(
            [
                #--------------------------
                # 6 COLUMNS left, Checklist
                #--------------------------
                html.Div(
                    [
                        html.H6('Choose Map Region:'),
                        dcc.Checklist(
                                id = 'regionControl',
                                options=[{'label': str(item), 'value': str(item)} for item in map_data['BoroName'].unique()],
                                value= [item for item in map_data['BoroName'].unique()],
                                labelStyle={'display': 'inline-block'}
                        ),
                    ],
                    className='six columns',
                    style={'marginTop': '20'}
                ),
                #--------------------------
                # 6 COLUMNS left, drop down
                #--------------------------
                html.Div(
                    [
                        html.H6('WIFI Type in Map:'),
                        dcc.Dropdown(
                            id='typeControl',
                            options= [{'label': str(item), 'value': str(item)} for item in map_data['Type'].unique()],
                            multi=True,
                            value=list(set(map_data['Type']))
                        )
                    ],
                    className='six columns',
                    style={'margin-top': '10'}
                )
            ],
            className='row'
        ),

        # Map + table + Histogram
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id='map-graph',
                                  animate=False)
                    ], className = "seven columns"
                ),

                html.Div([
                    dcc.Graph(
                        id='bar-graph',
                        figure = {
                            'data': [
                                go.Bar(
                                    x=Borough_counts_index,
                                    y=Borough_counts
                                )
                            ],
                            'layout': go.Layout(
                                title=go.layout.Title(text="Number of Wifi hotspot by block"),
                                xaxis={'title': 'Block Name', 'automargin': True},
                                yaxis={'title': 'Wifi Hotspot Count', 'automargin': True},
                                hovermode='closest',
                                autosize=True
                            )
                        }
                    )
                ], 
                className= 'five columns'
            )
            ], 
            className="row"
        )
    ], 
    className='ten columns offset-by-one')
)

"""
Callback functions
"""
# change scatter map based on checklist and dropdown
@app.callback(
    Output('map-graph', 'figure'),
    [Input('regionControl', 'value'),
     Input('typeControl', 'value')])
def map_selection(region, wifi_type):
    print("selected region", region)
    print("selected region", wifi_type)
    selected = map_data[map_data["BoroName"].isin(region)] # BoroName filter
    selected = selected[selected['Type'].isin(wifi_type)] # Type filter

    # function to set wifi hotspot color on the map based on the type
    def set_color(wifi_type):
        if wifi_type == 'Free': return 'green'
        elif wifi_type == 'Limited Free': return 'blue'
        else: return 'orange'

    # map data attribute
    data_map = [{
            "type": "scattermapbox",
            "lat": selected['Latitude'],
            "lon": selected['Longitude'],
            "hoverinfo": "text",
            "hovertext": [["Name: {} <br>Type: {} <br>Provider: {}".format(selected_name,selected_type,selected_provider)]
                        for selected_name,selected_type,selected_provider in zip(selected['Name'], 
                            selected['Type'], selected['Provider'])],
            "mode": "markers",
            "name": list(selected['Name']),
            "marker": {
                "size": 6,
                "opacity": 0.7,
                "color": list(map(set_color, selected['Type']))
            }
        }]
    figure = {
        "data": data_map,
        "layout": layout_map
    }
    return figure

# @app.callback(
#     Output('datatable', 'data'),
#     [Input('typeControl', 'value'),
#      Input('regionControl', 'value')])
# def update_selected_rows(typeControl, regionControl):
#     map_aux = map_data.copy()

#     # Type filter
#     map_aux = map_aux[map_aux['Type'].isin(typeControl)]
#     # regionControl filter
#     map_aux = map_aux[map_aux["Borough"].isin(regionControl)]

#     row = map_aux.to_dict('records')
#     return row

# @app.callback(
#     Output('bar-graph', 'figure'),
#     [Input('datatable', 'data'),
#      Input('datatable', 'selected_rows')])
# def update_figure(data, selected_rows):
#     dff = pd.DataFrame(data)

#     layout = go.Layout(
#         bargap=0.05,
#         bargroupgap=0,
#         barmode='group',
#         showlegend=False,
#         dragmode="select",
#         xaxis=dict(
#             showgrid=False,
#             nticks=50,
#             fixedrange=False
#         ),
#         yaxis=dict(
#             showticklabels=True,
#             showgrid=False,
#             fixedrange=False,
#             rangemode='nonnegative',
#             zeroline='hidden'
#         )
#     )

#     data = Data([
#          go.Bar(
#              x=dff.groupby('Borough', as_index = False).count()['Borough'],
#              y=dff.groupby('Borough', as_index = False).count()['Type']
#          )
#      ])

#     return go.Figure(data=data, layout=layout)

if __name__ == '__main__':
    app.run_server(debug=True)
