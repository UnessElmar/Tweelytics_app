import sys
import warnings

if not sys.warnoptions:
    warnings.simplefilter("ignore")
    
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from app import app
from panels import scraping, analysis

server = app.server


app.layout = html.Div(
    [
        html.Div(
            className="row header",
            children=[
                html.Button(id="menu", children=dcc.Markdown("&#8801")),
                html.Span(
                    className="app-title",
                    children=[
                        dcc.Markdown("**Tweelytics**"),
                        html.Span(
                            id="subtitle",
                            children=dcc.Markdown("&nbsp Scrap and analyze tweets"),
                            style={"font-size": "1.4rem", "margin-top": "26px", "margin-left": "26px"},
                        ),
                    ],
                ),
                #html.A(
                #    className="img",
                #    children=[
                #        html.Img(
                #            src=app.get_asset_url("logo.jpg"),
                #        ),
                #    ],
                #    target="_blank",
                #),
            ],
        ),
        html.Div(
            id="tabs",
            className="row tabs",
            children=[
                dcc.Link("Scraping", href="/tab-scrap"),
                dcc.Link("Analysis", href="/tab-analysis"),
            ],
        ),
        html.Div(
            id="mobile_tabs",
            className="row tabs",
            style={"display": "none"},
            children=[
                dcc.Link("Scraping", href="/tab-scrap"),
                dcc.Link("Analysis", href="/tab-analysis"),
            ],
        ),
        
        dcc.Location(id="url", refresh=False),
        html.Div(id="tab_content"),
        html.Link(
            href="https://use.fontawesome.com/releases/v5.2.0/css/all.css",
            rel="stylesheet",
        ),
        html.Link(
            href="https://fonts.googleapis.com/css?family=Dosis", rel="stylesheet"
        ),
        html.Link(
            href="https://fonts.googleapis.com/css?family=Open+Sans", rel="stylesheet"
        ),
    ],
    className="row",
    style={"margin": "0%"},
)


# Update the index

@app.callback(
    [
        Output("tab_content", "children"),
        Output("tabs", "children"),
    ],
    [Input("url", "pathname")],
)
def display_page(pathname):
    tabs = [
        dcc.Link("Scraping", href="/tab-scrap"),
        dcc.Link("Analysis", href="/tab-analysis"),
    ]
    if pathname == "/":
        tabs[0] = dcc.Link(
            dcc.Markdown("**&#9632 Scraping**"),
            href="/tab-scrap",
        )
    elif pathname == "/tab-scrap":
        tabs[0] = dcc.Link(
            dcc.Markdown("**&#9632 Scraping**"),
            href="/tab-scrap",
        )
        return scraping.layout, tabs
    elif pathname == "/tab-analysis":
        tabs[1] = dcc.Link(
            dcc.Markdown("**&#9632 Analysis**"), href="/tab-analysis"
        )
        return analysis.layout, tabs
    return scraping.layout, tabs


@app.callback(
    Output("mobile_tabs", "style"),
    [Input("menu", "n_clicks")],
    [State("mobile_tabs", "style")],
)
def show_menu(n_clicks, tabs_style):
    if n_clicks:
        if tabs_style["display"] == "none":
            tabs_style["display"] = "flex"
        else:
            tabs_style["display"] = "none"
    return tabs_style


if __name__ == "__main__":
    app.run_server(debug=True, dev_tools_ui=False, dev_tools_props_check=False)