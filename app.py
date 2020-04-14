import dash
import dash_html_components as html


app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}],
)

app.config.suppress_callback_exceptions = True