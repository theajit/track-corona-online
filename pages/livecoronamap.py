import dash
import json
from urllib.request import urlopen
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from apscheduler.schedulers.background import BackgroundScheduler
from app import app
from .functions import worlddata

token = open("/var/www/coronaApp/liveapp/pages/.mapbox_token").read()

url_world = "https://docs.google.com/spreadsheets/u/0/d/e/2PACX-1vR30F8lYP3jG7YOq8es0PBpJIE5yvRVZffOyaqC0GgMBN6yt0Q-NI8pxS7hd1F9dYXnowSC6zpZmW9D/pubhtml/sheet?headers=false&gid=0"
world_start = 7
world_strip = 2


def world_map_sensor():
    print("World Map Page Sensor Working!")
    return worlddata.return_world_map_df(url_world, world_start, world_strip)


world_sched = BackgroundScheduler(daemon=True)
world_sched.add_job(world_map_sensor, "interval", minutes=50)
world_sched.start()

df_country = world_map_sensor()

layout = html.Div(
    [
        html.Div(
            [html.H2("Live Corona Map")],
            style={"textAlign": "center", "padding-bottom": "30"},
        ),
        html.Div(
            [
                html.Span(
                    "Different cases to display : ",
                    className="six columns",
                    style={"text-align": "right", "width": "40%", "padding-top": 10},
                ),
                dcc.Dropdown(
                    id="value-selected",
                    value="Confirmed",
                    options=[
                        {"label": "Confirmed Cases ", "value": "Confirmed"},
                        {"label": "Deaths ", "value": "Deaths"},
                        {"label": "Serious & Critical ", "value": "Serious & Critical"},
                        {"label": "Recovered ", "value": "Recovered"},
                    ],
                    style={
                        "display": "block",
                        "margin-left": "auto",
                        "margin-right": "auto",
                        "width": "70%",
                    },
                    className="six columns",
                ),
            ],
            className="row",
        ),
        dcc.Graph(id="my-graph", config={"responsive": True, 'displayModeBar': False}),
    ],
    className="container",
)

with urlopen(
    "https://raw.githubusercontent.com/theajit/track-corona-online/master/assets/world.json"
) as response:
    world = json.load(response)

color1 = "#d2e3fc"
color2 = "#8ab4f8"
color3 = "#4285f4"
color4 = "#1967d2"
color5 = "#174ea6"

colormap = [
    [0.0, color1],
    [0.10, color2],
    [0.30, color3],
    [0.55, color4],
    [1.0, color5],
]


@app.callback(
    dash.dependencies.Output("my-graph", "figure"),
    [dash.dependencies.Input("value-selected", "value")],
)
def update_figure(selected):
    dff = (
        df_country.groupby(
            [
                "iso_alpha",
                "Country",
                "Confirmed",
                "Deaths",
                "Serious & Critical",
                "Recovered",
            ]
        )
        .max()
        .reset_index()
    )

    def title(text):
        if text == "Confirmed":
            return "Confirmed Cases"
        elif text == "Deaths":
            return "Deaths Cases"
        elif text == "Critical & Serious":
            return "Critical/Serious Cases"
        else:
            return "Recovered"

    trace = go.Choroplethmapbox(
        geojson=world,
        featureidkey="id",
        locations=dff.iso_alpha,
        z=dff[selected],
        text=dff["Country"],
        autocolorscale=False,
        colorscale=colormap,
    )
    return {
        "data": [trace],
        "layout": go.Layout(
            title=title(selected),
            mapbox_style="mapbox://styles/cocktailsguy/ck93b7muk22f61ipm39pag1oc",
            mapbox_accesstoken=token,
            mapbox_zoom=0.2,
            mapbox_center={"lat": 0, "lon": 0},
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
        ),
    }
