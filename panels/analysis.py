# -*- coding: utf-8 -*-
import os
import re
import base64
import codecs
from datetime import date, timedelta
import tweepy as tw
from twython import Twython
import pandas as pd

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

from app import app

from panels import graph_functions as gf
from panels import analysis_helpers as ah

usr_data_files = [{"label":filename[:-4], "value":os.path.join('data/user', filename)} for filename in os.listdir('data/user') if filename.endswith('.csv')]
hashtag_data_files = [{"label":filename[:-4], "value":os.path.join('data/hashtag', filename)} for filename in os.listdir('data/hashtag') if filename.endswith('.csv')]
all_data_files = usr_data_files + hashtag_data_files

# returns modal (hidden by default)
def modal():
    return html.Div(
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span(
                                    "New Analysis",
                                    style={
                                        "color": "#506784",
                                        "fontWeight": "bold",
                                        "fontSize": "20",
                                    },
                                ),
                                html.Span(
                                    "×",
                                    id="analysis_modal_close",
                                    n_clicks=0,
                                    style={
                                        "float": "right",
                                        "cursor": "pointer",
                                        "marginTop": "0",
                                        "marginBottom": "17",
                                    },
                                ),
                            ],
                            className="row",
                            style={"borderBottom": "1px solid #C8D4E3"},
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Div(
                                            id='option_ana_1',
                                            children=[
                                                html.P(
                                                    ["Select file"],
                                                    style={
                                                        "textAlign": "left",
                                                        "marginBottom": "2",
                                                        "marginTop": "4",
                                                    },
                                                ),
                                                dcc.Dropdown(
                                                    id="new_file_name",
                                                    options=all_data_files,
                                                    clearable=False,
                                                    value="all",
                                                    className="navbar",
                                                ),
                                            ],
                                        ),
                                        html.Div(
                                            id='option_ana_2',
                                            children=[
                                                html.P(
                                                    ["From date"],
                                                    style={
                                                        "textAlign": "left",
                                                        "marginBottom": "2",
                                                        "marginTop": "4",
                                                    },
                                                ),
                                                html.Div(
                                                    children=[
                                                        dcc.DatePickerSingle(
                                                            id="new_from_date",
                                                            #min_date_allowed=date.today() - timedelta(days=7),
                                                            max_date_allowed=date.today(),
                                                            initial_visible_month=date.today(),
                                                            display_format="DD/MM/YYYY",
                                                            date=date.today(),
                                                            #className='date',
                                                        ),
                                                        dcc.Input(
                                                            id="from_hour",
                                                            min="0",
                                                            max="23",
                                                            value="23",
                                                            type="number",
                                                            className="hour-picker",
                                                        ),
                                                        html.P('H', style={'display':'inline'}),
                                                        dcc.Input(
                                                            id="from_minute",
                                                            min="0",
                                                            max="59",
                                                            value="59",
                                                            type="number",
                                                            className="minute-picker",
                                                        ),
                                                        html.P('M', style={'display':'inline'}),
                                                    ],
                                                    className='row',
                                                ),
                                            ],
                                            style={"textAlign": "left"},
                                        
                                        ), 
                                        html.Div(
                                            id='option_ana_2bis',
                                            children=[
                                                html.P(
                                                    ["To date"],
                                                    style={
                                                        "textAlign": "left",
                                                        "marginBottom": "2",
                                                        "marginTop": "4",
                                                    },
                                                ),
                                                html.Div(
                                                    children=[
                                                        dcc.DatePickerSingle(
                                                            id="new_to_date",
                                                            #min_date_allowed=date.today() - timedelta(days=7),
                                                            max_date_allowed=date.today(),
                                                            initial_visible_month=date.today(),
                                                            display_format="DD/MM/YYYY",
                                                            date=date.today(),
                                                        ),
                                                        dcc.Input(
                                                            id="to_hour",
                                                            min="0",
                                                            max="23",
                                                            value="23",
                                                            type="number",
                                                            className="hour-picker",
                                                        ),
                                                        html.P('H', style={'display':'inline'}),
                                                        dcc.Input(
                                                            id="to_minute",
                                                            min="0",
                                                            max="59",
                                                            value="59",
                                                            type="number",
                                                            className="minute-picker",
                                                        ),
                                                        html.P('M', style={'display':'inline'}),
                                                    ],
                                                    className='row',
                                                ),
                                            ],
                                            style={"textAlign": "left"},
                                        ), 
                                        html.Div(
                                            id="option_ana_3",
                                            children=[
                                                html.P(
                                                    "Number of topics",
                                                    style={
                                                        "textAlign": "left",
                                                        "marginBottom": "2",
                                                        "marginTop": "4",
                                                    },
                                                ),
                                                dcc.Input(
                                                    id="new_number_topics",
                                                    placeholder="0",
                                                    type="number",
                                                    value="10",
                                                    min="0",
                                                    style={
                                                        "width": "100%",
                                                    },
                                                ),
                                            ]
                                        ),
                                    ],
                                    className="six columns",
                                    style={"paddingRight": "15"},
                                ),
                                html.Div(
                                    id='option_ana_4',
                                    children=[
                                        html.P(
                                            "Type of corpus",
                                            style={
                                                "textAlign": "left",
                                                "marginBottom": "2",
                                                "marginTop": "4",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            id="new_corpus_type",
                                            options=[
                                                {
                                                    "label": "Combined",
                                                    "value": "all",
                                                },
                                                {
                                                    "label": "N-grams",
                                                    "value": "select_n_gram",
                                                },
                                            ],
                                            value="all",
                                        ),
                                        html.Div(
                                            id="input_n_grams",
                                            style={"display": "none"},
                                            children=[
                                                html.P(
                                                    "N grams",
                                                    style={
                                                        "textAlign": "left",
                                                        "marginBottom": "2",
                                                        "marginTop": "4",
                                                    },
                                                ),
                                                dcc.Input(
                                                    id="new_n_grams",
                                                    placeholder="0",
                                                    type="number",
                                                    value="2",
                                                    min="1",
                                                    max="4",
                                                    style={
                                                        "width": "100%",
                                                    },
                                                ),
                                            ]
                                        )
                                        
                                    ],
                                    className="six columns",
                                    style={"paddingLeft": "15"},
                                ),
                            ],
                            className="row",
                            style={"paddingTop": "2%"},
                        ),
                        html.Br(),
                        html.Span(
                            "Submit",
                            id="submit_analysis_params",
                            n_clicks=0,
                            className="button button--primary",
                        ),
                    ],
                    className="modal-content",
                    style={"textAlign": "center"},
                )
            ],
            className="modal",
        ),
        id="analysis_modal",
        style={"display": "none"},
    )


layout = [
    html.Div(
        id="analysis_grid",
        children=[
            html.Span(
                "New analysis",
                id="new_analysis",
                n_clicks=0,
                className="button pretty_container",
            ),
        ],
    ),
    modal(),
    html.Br(),
    html.Div(
        id='div_history_display_mode',
        style={'display':'none'},
        children=[
            dcc.Dropdown(
                id="history_display_mode",
                options=[
                    {"label": "By hour", "value": "H"},
                    {"label": "By day", "value": "D"},
                ],
                value="D",
                clearable=False,
                #className='dropdown-normal',
            ),
        ],
    ),
    html.Div(
        id="div_history_n_hours",
        style={'display':'none'},
        children=[
            dcc.Input(
                id="history_n_hours",
                type='number',
                min='1',
                max='24',
                value='24',
            ),
            html.P('Hours', style={'display':'inline'}),
        ],
    ),
    html.Div(
        children=[
            dcc.Loading(
                className="lds-ripple",
                type="graph",
                children=[
                    html.Div(
                        id="loading_ana_output",
                        children=[
                            html.Div(
                                id='history_block',
                                style={'display':'none'},
                                children=[
                                    html.Div(
                                        dcc.Graph(
                                            id="history_graph",
                                            style={"height": "90%", "width": "100%"},
                                            config=dict(displayModeBar=False),
                                        ),
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            dcc.Loading(
                className="lds-ripple",
                children=[
                    html.Div(
                        id="loading_ana_output_bis",
                        children=[
                            html.Div(
                                id='header_collapse',
                                style={
                                    'display':'none',
                                },
                                children=[
                                    html.H1(
                                        'Topics WordCloud',
                                        style={
                                            'display':'inline',
                                        },
                                    ),
                                    html.Span(
                                        "",
                                        id="collapse_wordcloud",
                                        n_clicks=0,
                                        style={
                                            'color':'white',
                                            "width":'2%',
                                            "float":"left",
                                            'height':'27px',
                                            "cursor":"pointer",
                                            "background-color":'#8758df',
                                            "text-align":"center"
                                        },
                                    ),
                                ],
                                className='row',
                            ),                            
                            html.Div(
                                id='word_cloud_block',
                            ),

                            html.Div(
                                id='header_lda_collapse',
                                style={
                                    'display':'none',
                                },
                                children=[
                                    html.H1(
                                        'Topics LDA Visualization',
                                        style={
                                            'display':'inline',
                                        },
                                    ),
                                    html.Span(
                                        "",
                                        id="collapse_lda",
                                        n_clicks=0,
                                        style={
                                            'color':'white',
                                            "width":'2%',
                                            "float":"left",
                                            'height':'27px',
                                            "cursor":"pointer",
                                            "background-color":'#8758df',
                                            "text-align":"center"
                                        },
                                    ),
                                ],
                                className='row',
                            ),                            
                            html.Div(
                                id='lda_block',
                            ),
                        ],
                    ),
                ],
            ),                    
        ],
    ),
]





###############################################################################################
#                                       CALLBACKS                                             #
###############################################################################################

# hide/show modal
@app.callback(
    Output("analysis_modal", "style"), [Input("new_analysis", "n_clicks")]
)
def display_opportunities_modal_callback(n):
    if n > 0:
        return {"display": "block"}
    return {"display": "none"}


# hide/show number of tweets
@app.callback(
    Output("input_n_grams", "style"), [Input("new_corpus_type", "value")]
)
def display_ngrams_modal_callback(q_type):
    if q_type == 'select_n_gram':
        return {"display": "inline"}
    return {"display": "none"}

# reset to 0 add button n_clicks property
@app.callback(
    Output("new_analysis", "n_clicks"),
    [
        Input("analysis_modal_close", "n_clicks"),
        Input("submit_analysis_params", "n_clicks"),
    ],
)
def close_ana_modal_callback(n, n2):
    return 0


# update filenames
@app.callback(
    Output("new_file_name", "options"),
    [
        Input("new_analysis", "n_clicks"),
    ],
)
def close_ana_modal_callback(n):
    if n:
        usr_data_files = [{"label":filename[:-4], "value":os.path.join('data/user', filename)} for filename in os.listdir('data/user') if filename.endswith('.csv')]
        hashtag_data_files = [{"label":filename[:-4], "value":os.path.join('data/hashtag', filename)} for filename in os.listdir('data/hashtag') if filename.endswith('.csv')]
        new_files = usr_data_files + hashtag_data_files
        return new_files
    return all_data_files

@app.callback(
    [
        Output('history_graph', 'figure'),
        Output('history_block', 'style'),
        Output('header_collapse', 'style'),
        Output('header_lda_collapse', 'style'),
    ],
    [
        Input('submit_analysis_params', 'n_clicks'),
        Input('history_display_mode', 'value'),
        Input('history_n_hours', 'value'),
    ],
    [
        State('new_file_name', 'value'),
        State('new_from_date', 'date'),
        State('from_hour', 'value'),
        State('to_minute', 'value'),
        State('new_to_date', 'date'),
        State('to_hour', 'value'),
        State('to_minute', 'value'),
    ],
)
def plot_tweets_history(n, by_param, n_hour, csv_file, from_date, from_hour, from_min, to_date, to_hour, to_min):
    if n and (by_param or n_hour):
        df_temp = pd.read_csv(csv_file, sep=';')
        if len(str(from_hour)) == 1:
            from_hour = '0' + str(from_hour)
        if len(str(to_hour)) == 1:
            to_hour = '0' + str(to_hour)
        if len(str(from_min)) == 1:
            from_min = '0' + str(from_min)
        if len(str(to_min)) == 1:
            to_min = '0' + str(to_min)

        from_instance = str(from_date) + ' ' + str(from_hour) + ':' + str(from_min) + ':00'
        to_instance = str(to_date) + ' ' + str(to_hour) + ':' + str(to_min) + ':00'
        return gf.tweets_history(df_temp, from_instance, to_instance, by_param, n_hour), {'display':'block'}, {'display':'block'}, {'display':'block'}
    return {"data": None, "layout": None}, {'display':'none'}, {'display':'none'}, {'display':'none'}


# hide mode dropdown
@app.callback(
    Output('div_history_display_mode', 'style'),
    [Input('submit_analysis_params', 'n_clicks'),]
)
def show_nbins(n):
    if n:
        return {'display':'block', "margin-bottom":'10px'}
    return {'display':'none'}

# hide show n bins
@app.callback(
    Output('div_history_n_hours', 'style'),
    [
        Input('submit_analysis_params', 'n_clicks'),
        Input('history_display_mode', 'value'),
    ]
)
def show_nbins(n, d_mode):
    if n:
        if d_mode == 'H':
            return {'display':'block', "margin-bottom":'10px'}
        elif d_mode == 'D':
            return {'display':'none'}
    return {'display':'none'}
    
# Display wordcloud and ldaviz
@app.callback(
    [
        Output('word_cloud_block', 'children'),
        Output('lda_block', 'children'),
    ],
    [Input('submit_analysis_params', 'n_clicks'),],
    [
        State('new_file_name', 'value'),
        State('new_from_date', 'date'),
        State('from_hour', 'value'),
        State('to_minute', 'value'),
        State('new_to_date', 'date'),
        State('to_hour', 'value'),
        State('to_minute', 'value'),
        State('new_corpus_type', 'value'),
        State('new_n_grams', 'value'),
        State('new_number_topics', 'value'),
    ],
)
def display_graphs(n, csv_file, from_date, from_hour, from_min, to_date, to_hour, to_min, corp_type, n_gram, n_topics, ):
    if n:
        if len(str(from_hour)) == 1:
            from_hour = '0' + str(from_hour)
        if len(str(to_hour)) == 1:
            to_hour = '0' + str(to_hour)
        if len(str(from_min)) == 1:
            from_min = '0' + str(from_min)
        if len(str(to_min)) == 1:
            to_min = '0' + str(to_min)

        from_instance = str(from_date) + ' ' + str(from_hour) + ':' + str(from_min) + ':00'
        to_instance = str(to_date) + ' ' + str(to_hour) + ':' + str(to_min) + ':00'
        df = ah.read_tweets(csv_file, from_instance, to_instance)
        if corp_type == 'all':
            [corpus, words] = ah.build_combined_corpus(df)
        elif corp_type == 'select_n_gram':
            [corpus, words] = ah.build_ngram_corpus(df, int(n_gram))
        lda_model = ah.lda_model(corpus, words, n_topics)
        gf.wordcould(lda_model, n_topics)
        gf.ldaPlot(lda_model, corpus)
        encode_img = base64.b64encode(open('data/temp/plot.jpg', 'rb').read()).decode('ascii')
        out1 = html.Div(
            [
                html.Div(
                    html.Img(
                        src='data:temp/jpg;base64,{}'.format(encode_img),
                        className="wordcloud-img",
                    ),
                ),
            ],
        )
        html_file = codecs.open("data/temp/lda.html", "r", "utf-8")
        html_file = html_file.read()
        out2 = html.Iframe(
            srcDoc=html_file,
            width="100%",
            height='1200px',
        )
        return out1, out2
    return None, None

# collapse wordcloud
@app.callback(
    Output('word_cloud_block', 'style'),
    [Input('collapse_wordcloud', 'n_clicks')],
)
def collapse_function(n):
    if n:
        if n%2:
            return {'display':'none'}
        else:
            return {'display':'block'}
    return {'display':'block'}


# collapse lda viz
@app.callback(
    Output('lda_block', 'style'),
    [Input('collapse_lda', 'n_clicks')],
)
def collapse_function(n):
    if n:
        if n%2:
            return {'display':'none'}
        else:
            return {'display':'block'}
    return {'display':'block'}

# add analysis indicators
# fix min max dates based on each file