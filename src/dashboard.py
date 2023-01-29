import dash
from dash import dcc, html
from dash.dependencies import Output, Input, State
import plotly.express as px
import dash_bootstrap_components as dbc

import pandas as pd

import pickle

from itertools import islice


from collections import OrderedDict, defaultdict
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta, FR

import os


# Define app
# VAPOR, LUX, QUARTZ
# external_stylesheets=[dbc.themes.QUARTZ]
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], meta_tags=[{'name': 'viewport','content': 'width=device-width, initial-scale=1.0'}])
app.title = "DS Groups"
server = app.server
# Define callbacks

navbar = dbc.NavbarSimple(
    # brand="DSG Peer Group Generator",
    brand_href="#",
    color="success",
    dark=True,
    id = "navbar-example-update"
)


print("hi from global")


########## UTILITY FUNCTIONS ###############################
def generate_cards(date, groups, card_num_cols):
    
    len_groups = len(list(groups))
    
    # Use islice
    def convert(listA, len_2d):
        res = iter(listA)
        return [list(islice(res,i)) for i in len_2d]
    
    # this list helps dynamically display layout of the cards
    res = convert(list(groups), [card_num_cols]*(len_groups//card_num_cols) + [len_groups%card_num_cols])
    
    # get card body
    cards_body = []
    for r in res:
        row_list = []
        for c in list(r):
            
            card_content = [dbc.CardBody(html.H5(", ".join(list(c)), className="card-title"))]
            
            row_list.append(dbc.Col(dbc.Card(card_content, color = "success", inverse=True), 
                # TODO: improve how we specify responsiveness
                width = 12//card_num_cols, lg = 4, md = 12, sm = 12, xs = 12))
            
        cards_body.append(dbc.Row(row_list, className="mb-4", justify="center"))
    
    cards = html.Div( [dbc.Row([html.H1(date)])]+ cards_body)

    return cards

def convert_from_fz_to_str(g):
    res = ""
    for elem in list(g):
        res += ",".join(list(elem))
        res += "; "
    return res

def convert_from_str_to_fz(s):
    res = s.split("; ")[:-1]
    res2 = []
    for elem in res:
        res2.append(frozenset(elem.split(",")))
    return frozenset(res2)

def read_history()->dict:
    """
    Description:
        Read history from pickled object
    Args:
    Returns: 
        history (dict of datetime.date: frozenset(frozenset)): 
            the history of past groups
    """
    with open('data/history.pickle', 'rb') as handle:
        history = pickle.load(handle)
    handle.close()
    return history

#############################################################

cards = html.Div(id="cards")


# app.layout = [navbar, dbc.Container()]
app.layout = html.Div([navbar, dcc.Store(id="cards-input", data=""),
                        dbc.Container(
                            [cards],
                            style = {
                            "margin-top": "5%", "margin-bottom": "5%",
                            },

                        )
                    ])


@app.callback(
    Output("cards", "children"), [Input("cards-input", "data")]
)
def get_data_and_cards(data_input):

    print("read history")
    history = read_history()

    most_recent_date = sorted(history.keys())[-1]
    most_recent_group = history[most_recent_date]
    
    newlist = [most_recent_date, most_recent_date + relativedelta(weekday=FR(+2))]
    
    date = " to ".join([str(x) for x in newlist])
    
    # can parametrize this later if necessary
    card_num_cols = 3
    
    # generate cards
    cards = generate_cards(date = date, 
                groups = most_recent_group,
                card_num_cols = card_num_cols
            )
    
    return cards
    
    


    
if __name__=='__main__':
    app.run_server(debug=True, port=8080)
