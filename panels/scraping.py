# -*- coding: utf-8 -*-
import os
import re
from datetime import date, timedelta
import tweepy as tw
from twython import Twython
import pandas as pd

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

from app import app

from dotenv import load_dotenv

project_folder = os.path.expanduser('~/tweelytics_app')  
load_dotenv(os.path.join(project_folder, '.env'))

# access to tweepy API
consumer_key_mentions = os.getenv('consumer_key_mentions')
consumer_secret_mentions = os.getenv('consumer_secret_mentions')
access_token_mentions = os.getenv('access_token_mentions')
access_token_secret_mentions = os.getenv('access_token_secret_mentions')

auth = tw.OAuthHandler(consumer_key_mentions, consumer_secret_mentions)
auth.set_access_token(access_token_mentions, access_token_secret_mentions)
api = tw.API(auth, wait_on_rate_limit=True)

api_twython = Twython(consumer_key_mentions, consumer_secret_mentions, access_token_mentions, access_token_secret_mentions)

# scrap tweets of specific user
def scrap_usr_tweets(userID, scrap_type, nbr_tweets):
    if scrap_type == 'all':
        tweets = api.user_timeline(
            screen_name=userID,
            count=200,
            tweet_mode = 'extended',
        )
    elif scrap_type != 'all':
        tweets = api.user_timeline(
            screen_name=userID, 
            count=nbr_tweets,
            tweet_mode = 'extended',
        )
    details = api_twython.show_user(screen_name=userID)
    real_name = details['name']
    img_url = details['profile_image_url_https']
    img_url = img_url.replace('_normal', '')
    bio = details['description']
    n_followers = details['followers_count']

    tweets_info = [[tweet.created_at, tweet.favorite_count, tweet.retweet_count, tweet.full_text] for tweet in tweets]
    df_tweets = pd.DataFrame(data=tweets_info, 
                    columns=['date', 'likes', 'retweets', 'tweet'])
    return df_tweets, img_url, real_name, bio, n_followers

# scrap tweets of all users
def scrap_tweets(search_words, lang, geo, date_since, scrap_type, n_tweets):
    search_words = search_words.split(' ')
    print(search_words)
    if lang == 'all':
        lang = None
    if geo == 'all':
        geo = None
    if scrap_type == 'all':
        tweets = tw.Cursor(api.search,
                    q=search_words,
                    lang=lang,
                    geocode=geo,
                    tweet_mode='extended',
                    since=date_since).items()
    if scrap_type != 'all':
        n_tweets = int(n_tweets)
        tweets = tw.Cursor(api.search,
                    q=search_words,
                    lang=lang,
                    geocode=geo,
                    tweet_mode='extended',
                    since=date_since).items(n_tweets)
    tweets_info = [[tweet.user.screen_name, tweet.created_at, tweet.full_text] for tweet in tweets]
    df_tweets = pd.DataFrame(data=tweets_info, 
                    columns=['user', 'date', 'tweet'])
    return df_tweets


# create user card
def create_card(image, real_name, user_name, nbr_followers, bio):
    return dbc.Card(
        className='card',
        children=[
            dbc.CardImg(
                src=image,
                top=True,
                className="card-img",
            ),
            dbc.CardBody(
                [
                    html.H4(real_name, className="card-title"),
                    html.H4(user_name, className="card-subtitle"),
                    html.H4('{} followers'.format(str(nbr_followers)), className="card-number"),
                    html.P(
                        bio,
                        className="card-text",
                    ),
                    html.A(
                        target="_blank",
                        href="https://twitter.com/" + user_name,
                        children=[
                            dbc.Button(
                                "Visit account",
                                className="button",
                            ),
                        ]
                    ),
                ],
            ),
        ],
    )

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
                                    "New query",
                                    style={
                                        "color": "#506784",
                                        "fontWeight": "bold",
                                        "fontSize": "20",
                                    },
                                ),
                                html.Span(
                                    "×",
                                    id="scraps_modal_close",
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
                                        dbc.ButtonGroup(
                                            children=[
                                                dbc.Button(
                                                    "All users",
                                                    id='all_users_button',
                                                    n_clicks=0,
                                                    className="button-user1",
                                                ),
                                                dbc.Button(
                                                    "By user ID",
                                                    id='one_user_button',
                                                    n_clicks=0,
                                                    className="button-user2",
                                                ),
                                            ],
                                        ),
                                        html.Div(
                                            id='user_input',
                                            style={"display": "none"},
                                            children=[
                                                html.P(
                                                    ["User ID"],
                                                    style={
                                                        "float": "left",
                                                        "marginTop": "4",
                                                        "marginBottom": "2",
                                                    },
                                                    className="row",
                                                ),
                                                dcc.Input(
                                                    id="new_user_name",
                                                    placeholder="Example: realDonaldTrump",
                                                    type="text",
                                                    value="",
                                                    style={"width": "100%"},
                                                ),
                                            ],
                                        ),
                                        html.Div(
                                            id='option_1',
                                            style={'display':'none'},
                                            children=[
                                                 html.P(
                                                    ["Hashtag"],
                                                    style={
                                                        "float": "left",
                                                        "marginTop": "4",
                                                        "marginBottom": "2",
                                                    },
                                                    className="row",
                                                ),
                                                dcc.Input(
                                                    id="new_hashtag_name",
                                                    placeholder="#Hashtag1 #Hashtag2 #Hashtag3 ...",
                                                    type="text",
                                                    value="",
                                                    style={"width": "100%"},
                                                ),
                                            ],
                                        ),
                                       

                                        html.Div(
                                            id='option_2',
                                            style={'display':'none'},
                                            children=[
                                                html.P(
                                                    ["Localisation"],
                                                    style={
                                                        "textAlign": "left",
                                                        "marginBottom": "2",
                                                        "marginTop": "4",
                                                    },
                                                ),
                                                dcc.Dropdown(
                                                    id="new_localisation",
                                                    options=[
                                                        {
                                                            "label": "All",
                                                            "value": "all",
                                                        },
                                                        {
                                                            "label": "France",
                                                            "value": "46.465349,2.156153,680km",
                                                        },
                                                    ],
                                                    clearable=False,
                                                    value="all",
                                                ),
                                            ],
                                        ),
                                        

                                        html.Div(
                                            id='option_3',
                                            style={'display':'none'},
                                            children=[
                                                html.P(
                                                    "Language",
                                                    style={
                                                        "textAlign": "left",
                                                        "marginBottom": "2",
                                                        "marginTop": "4",
                                                    },
                                                ),
                                                dcc.Dropdown(
                                                    id="new_scrap_lang",
                                                    options=[
                                                        {
                                                            "label": "French",
                                                            "value": "fr",
                                                        },
                                                        {
                                                            "label": "English",
                                                            "value": "en",
                                                        }
                                                    ],
                                                    value="fr",
                                                ),
                                            ],
                                        ),
                                        
                                        html.Div(
                                            id='option_4',
                                            style={'display':'none'},
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
                                                    dcc.DatePickerSingle(
                                                        id="new_scrap_date",
                                                        min_date_allowed=date.today() - timedelta(days=7),
                                                        max_date_allowed=date.today(),
                                                        initial_visible_month=date.today(),
                                                        display_format="DD/MM/YYYY",
                                                        date=date.today(),
                                                    ),
                                                    style={"textAlign": "left"},
                                                ),
                                            ],
                                        ),                                        
                                    ],
                                    className="six columns",
                                    style={"paddingRight": "15"},
                                ),
                                html.Div(
                                    id='option_5',
                                    children=[
                                        html.P(
                                            "Type of query",
                                            style={
                                                "textAlign": "left",
                                                "marginBottom": "2",
                                                "marginTop": "4",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            id="new_scrap_type",
                                            options=[
                                                {
                                                    "label": "All tweets",
                                                    "value": "all",
                                                },
                                                {
                                                    "label": "Restrict number of tweets",
                                                    "value": "n_items",
                                                },
                                            ],
                                            value="all",
                                        ),
                                        html.Div(
                                            id="number_tweets",
                                            style={"display": "none"},
                                            children=[
                                                html.P(
                                                    "Number of tweets",
                                                    style={
                                                        "textAlign": "left",
                                                        "marginBottom": "2",
                                                        "marginTop": "4",
                                                    },
                                                ),
                                                dcc.Input(
                                                    id="new_number_tweets",
                                                    placeholder="0",
                                                    type="number",
                                                    value="10",
                                                    min="0",
                                                    style={
                                                        "width": "100%",
                                                    },
                                                ),
                                            ]
                                        )
                                        
                                    ],
                                    className="six columns",
                                    style={"paddingLeft": "15", 'display':'none'},
                                ),
                            ],
                            className="row",
                            style={"paddingTop": "2%"},
                        ),
                        html.Br(),
                        html.Span(
                            "Submit",
                            id="submit_scrap_params",
                            #style={'display':'none'},
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
        id="scraps_modal",
        style={"display": "none"},
    )


layout = [
    html.Div(
        id="scraping_grid",
        children=[
            html.Span(
                "New query",
                id="new_scrap",
                n_clicks=0,
                className="button pretty_container",
            ),
        ],
    ),
    modal(),
    html.Br(),
    html.Div(
        children=[
            dcc.Store(id='memory'),
            dcc.Loading(
                className="lds-ripple",
                type="default",
                children=[
                    html.Div(
                        id="loading_output",
                        children=[
                            html.Div(
                                id="opportunity_indicators",
                                className="row indicators",                                
                            ),
                            html.Br(),
                            html.Span(
                                "DOWNLOAD FILE",
                                id="download_file",
                                style={'display':'none'},
                                n_clicks=0,
                                className="button-download",
                            ),
                            html.Br(),
                            dbc.Alert(
                                "File downloaded",
                                id="alert_download",
                                is_open=False,
                                duration=3000,
                                className='alert',
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
    Output("scraps_modal", "style"), [Input("new_scrap", "n_clicks")]
)
def display_opportunities_modal_callback(n):
    if n > 0:
        return {"display": "block"}
    return {"display": "none"}

# hide/show options
@app.callback(
    [
        Output("option_1", "style"),
        Output("option_2", "style"),
        Output("option_3", "style"),
        Output("option_4", "style"),
        Output("submit_scrap_params", "style"),
        Output("option_5", "style"),
    ],
    [
        Input("all_users_button", "n_clicks"),
        Input("one_user_button", "n_clicks"),
    ]
)
def display_options(n1, n2):
    old_style = {'display':'none'}
    if n1 > 0:
        new_style = {'display':'inline'}
        submit_new_style = {'margin':'0 auto', 'display':'block'}
        new_style_1 = {"paddingLeft": "15", 'display':'inline'}
        return new_style, new_style, new_style, new_style, submit_new_style, new_style_1
    elif n2 > 0:
        new_style = {'display':'inline'}
        submit_new_style = {'margin':'0 auto', 'display':'block'}
        new_style_1 = {"paddingLeft": "15", 'display':'inline'}
        return old_style, old_style, old_style, old_style, submit_new_style, new_style_1
    return old_style, old_style, old_style, old_style, old_style, old_style



# hide/show user ID
@app.callback(
    Output("user_input", "style"),
    [
        Input("all_users_button", "n_clicks"),
        Input("one_user_button", "n_clicks"),
    ]
)
def display_user_id(n1, n2):
    if n1 > 0:
        return {"display": "none"}
    if n2 > 0:
        return {"display": "inline"}
    return {"display": "none"}

# update user filter clicks 1
@app.callback(
    Output("all_users_button", "n_clicks"),
    [Input("one_user_button", "n_clicks")],
)
def display_user_id1(n1):
    return 0
    

# update all users filter color
@app.callback(
    [
        Output("all_users_button", "style"),
        Output("one_user_button", "style"),
    ],    
    [
        Input("all_users_button", "n_clicks"),
        Input("one_user_button", "n_clicks"),
    ]
)
def update_style(n1, n2):
    triggered_btn = dash.callback_context.triggered[0]
    if triggered_btn['prop_id'] == 'all_users_button.n_clicks':
        if triggered_btn['value'] > 0:
            return {"background-color": "#310288"}, {"background-color": "#8758df"} 
        else:
            if n2 > 0:
                return {"background-color": "#8758df"}, {"background-color": "#310288"}
    return {"background-color": "#8758df"}, {"background-color": "#8758df"} 

# hide/show number of tweets
@app.callback(
    Output("number_tweets", "style"), [Input("new_scrap_type", "value")]
)
def display_opportunities_modal_callback(q_type):
    if q_type == 'n_items':
        return {"display": "inline"}
    return {"display": "none"}

# reset to 0 add button n_clicks property
@app.callback(
    Output("new_scrap", "n_clicks"),
    [
        Input("scraps_modal_close", "n_clicks"),
        Input("submit_scrap_params", "n_clicks"),
    ],
)
def close_modal_callback(n, n2):
    return 0

# launch tweets scrap and show info
@app.callback(
    [
        Output('memory', 'data'),
        Output("opportunity_indicators", "children"),
        Output('download_file', 'style'),
    ],
    [
        Input('submit_scrap_params', 'n_clicks'),
        Input('download_file', 'n_clicks'),
    ],
    [
        State('new_user_name', 'value'),
        State('new_hashtag_name', 'value'),
        State('new_localisation', 'value'),
        State('new_scrap_lang', 'value'),
        State('new_scrap_date', 'date'),
        State('new_scrap_type', 'value'),
        State('new_number_tweets', 'value'),
        State("all_users_button", "n_clicks"),
        State("one_user_button", "n_clicks"),
    ]
)
def launch_scrap(n, n_downlaod, usr_name, hashtags, geo_loc, language, from_date, type_scrap, nbr_tweets, n1, n2):
    if n > 0:
        if n1 > 0:
            tweets = scrap_tweets(hashtags, str(language), str(geo_loc), str(from_date), str(type_scrap), str(nbr_tweets))
            n_tweets = len(tweets)
            date_1 = str(tweets.date.min()).replace('-', '/')
            date_2 = str(tweets.date.max()).replace('-', '/')
            childs = [
                html.Div(
                    [
                        html.P(dcc.Markdown("**{}**".format(n_tweets)), className="indicator_value"),
                        html.P("Tweets", className="twelve columns indicator_text"),
                    ],
                    className="four columns indicator pretty_container",
                ),
                html.Div(
                    [
                        html.P("From", className="twelve columns indicator_text"),
                        html.P(dcc.Markdown("**{}**".format(date_1)), className="indicator_value"),
                    ],
                    className="four columns indicator pretty_container",
                ),
                html.Div(
                    [
                        html.P("To", className="twelve columns indicator_text"),
                        html.P(dcc.Markdown("**{}**".format(date_2)), className="indicator_value"),
                    ],
                    className="four columns indicator pretty_container",
                ),
            ]
        elif n2 > 0:
            [tweets, img_url, real_name, bio, n_followers] = scrap_usr_tweets(str(usr_name), str(type_scrap), str(nbr_tweets))
            n_tweets = len(tweets)
            date_1 = str(tweets.date.min()).replace('-', '/')
            date_2 = str(tweets.date.max()).replace('-', '/')
            childs = [
                html.Div(
                    [
                        create_card(
                            img_url,
                            real_name,
                            usr_name,
                            n_followers,
                            bio,
                        ),
                    ],
                    className="six columns",
                ),
                html.Div(
                    [
                        html.P(dcc.Markdown("**{}**".format(n_tweets)), className="indicator_value"),
                        html.P("Tweets", className="twelve columns indicator_text"),
                    ],
                    className="three columns indicator pretty_container",
                ),
                html.Div(
                    [
                        html.P("From", className="twelve columns indicator_text"),
                        html.P(dcc.Markdown("**{}**".format(date_1)), className="indicator_value"),
                    ],
                    className="three columns indicator pretty_container",
                ),
                html.Div(
                    [
                        html.P("To", className="twelve columns indicator_text"),
                        html.P(dcc.Markdown("**{}**".format(date_2)), className="indicator_value"),
                    ],
                    className="three columns indicator pretty_container",
                ),
            ]
        if n_downlaod:
            if dash.callback_context.triggered[0]['prop_id'] == 'download_file.n_clicks':
                return tweets.to_json(orient="split"), childs, {'display':'none'}
        return tweets.to_json(orient="split"), childs, {'display':'block'}
    return None, None, {'display':'none'}

# download csv of scrapped tweets
@app.callback(
    Output("alert_download", "is_open"),
    [
        Input("download_file", "n_clicks"),
    ],
    [
        State("memory", "data"),
        State("alert_download", "is_open"),
        State('new_user_name', 'value'),
        State('new_hashtag_name', 'value'),
    ],
)
def toggle_alert(n, tweets, is_open, usr_name, hashtags):
    if n:
        tweets = pd.read_json(tweets, orient="split")
        from_date = str(tweets.date.min()).split(' ')[0].replace('-', '_')
        to_date = str(tweets.date.max()).split(' ')[0].replace('-', '_')
        if usr_name:
            relative_filename = os.path.join(
                'data',
                'user',
                '{}_tweets_from_{}_to_{}.csv'.format(usr_name, from_date, to_date)
            )
        elif hashtags:
            hashtags = hashtags.replace("#", '')
            hashtags = hashtags.replace(" ", '_')
            relative_filename = os.path.join(
                'data',
                'hashtag',
                '{}_tweets_from_{}_to_{}.csv'.format(hashtags, from_date, to_date)
            )
        absolute_filename = os.path.join(os.getcwd(), relative_filename)
        tweets.to_csv(absolute_filename, sep=';', index=False)
        return not is_open
    return is_open


# reset query values
@app.callback(
    [
        Output('new_user_name', 'value'),
        Output('new_hashtag_name', 'value'),
        Output('new_localisation', 'value'),
        Output('new_scrap_lang', 'value'),
        Output('new_scrap_date', 'date'),
        Output('new_scrap_type', 'value'),
        Output('new_number_tweets', 'value'),
    ],
    [
        Input('download_file', 'n_clicks'),
    ]
)
def reset_values(n):
    return None, None, 'all', 'fr', date.today(), 'all', None