# import der benoetigten pakete
import pandas as pd
import plotly.express as px
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

# datenimport
df = pd.read_excel("query_short.xlsx")
# kopie datengrundlage
dff = df.copy()
# extraktion ereignis-filterauswahl
quake_type = dff["type"].unique()
# definition des app-layouts
app.layout = html.Div([

    # dashboard-titel
    html.H1("Weltweite Erdbebenereignisse des Jahres 2021", style={'text-align': 'center'}),
    # erklärtext
    html.P("Dieses interaktive Dashboard ermöglicht die visuelle Exploration und Analyse von weltweiten "
           "Erdbebenereignissen des Jahres 2021. Die insgesamt rund 160'000 Ereignisse mit einer Magnitude "
           "von mindestens 0 wurden vom amerikanischen «Earthquake-Hazards-Programm» (https://earthquake.usgs.gov/) "
           "bezogen und im Rahmen des Kurses «Advanced Data Visualisation» an der Fachhochschule Graubünden für das "
           "vorliegende Dashboard aufbereitet. Zur Exploration und Analyse des Datensatzes stehen insgesamt "
           "drei Filteroptionen und fünf Visualisierungen zur Verfügung.", style={'text-align': 'center'}),

    html.Br(),
    html.Hr(),

    # magnituden-slider
    html.H4("Erdbebenstärke", style={'text-align': 'center'}),
    html.P("Hier kann der gewünschte Magnitudenbereich eingestellt werden:",
           style={'text-align': 'center'}),
    dcc.RangeSlider(id="mag-slider",
                    min=dff["mag"].min(),
                    max=dff["mag"].max(),
                    step=0.1,
                    value=[4.5, dff["mag"].max()],
                    tooltip={"placement": "bottom", 'always_visible': False},
                    marks={0.0: '0.0',
                           0.5: '0.5',
                           1.0: '1.0',
                           1.5: '1.5',
                           2.0: '2.0',
                           2.5: '2.5',
                           3.0: '3.0',
                           3.5: '3.5',
                           4.0: '4.0',
                           4.5: '4.5',
                           5.0: '5.0',
                           5.5: '5.5',
                           6.0: '6.0',
                           6.5: '6.5',
                           7.0: '7.0',
                           7.5: '7.5',
                           8.0: '8.0',
                           8.5: '8.5'}),

    # monats-filter
    html.H4("Monatsauswahl", style={'text-align': 'center'}),
    html.P("Hier kann die gewünschte Zeitspanne eingestellt werden:",
           style={'text-align': 'center'}),
    dcc.RangeSlider(id='months',
                    min=dff["month"].min(),
                    max=dff["month"].max(),
                    value=[1, 6],
                    dots=False,
                    marks={
                        1: {'label': 'Januar'},
                        2: {'label': 'Februar'},
                        3: {'label': 'März'},
                        4: {'label': 'April'},
                        5: {'label': 'Mai'},
                        6: {'label': 'Juni'},
                        7: {'label': 'Juli'},
                        8: {'label': 'August'},
                        9: {'label': 'September'},
                        10: {'label': 'Oktober'},
                        11: {'label': 'November'},
                        12: {'label': 'Dezember'}
                    },
                    allowCross=False,
                    tooltip={"placement": "bottom", 'always_visible': False},
                    disabled=False,
                    step=1),

    # ereignis-filter
    html.H4("Ereignisauswahl", style={'text-align': 'center'}),
    html.P("Hier können die gewünschten Ereignisarten ausgewählt werden:",
           style={'text-align': 'center'}),
    dcc.Dropdown(id='type',
                 options=[{"label": x, "value": x} for x in quake_type],
                 multi=True,
                 clearable=True,
                 value=["Erdbeben"]),

    html.Br(),
    html.Hr(),
    html.H2("Visualisierungen", style={'text-align': 'center'}),

    # weltkarte
    dcc.Graph(id='map', figure={},
              style={'display': 'inline-block', 'vertical-align': 'top', 'width': '100%'}),

    html.Br(),

    # tages-balkendiagramm
    dcc.Graph(id='barchart', figure={},
              style={'display': 'inline-block', 'vertical-align': 'top', 'width': '40%'}),
    # geo-scatterplot
    dcc.Graph(id='scatter', figure={},
              style={'display': 'inline-block', 'vertical-align': 'top', 'width': '40%'}),
    # ereignis-piechart
    dcc.Graph(id='pie', figure={},
              style={'display': 'inline-block', 'vertical-align': 'top', 'width': '20%'}),
    # matrix
    dcc.Graph(id='matrix', figure={},
              style={'display': 'inline-block', 'vertical-align': 'top', 'width': '100%'})
])


@app.callback(
    [Output(component_id="map", component_property='figure'),
     Output(component_id="barchart", component_property='figure'),
     Output(component_id="scatter", component_property='figure'),
     Output(component_id="pie", component_property='figure'),
     Output(component_id="matrix", component_property='figure')],
    [Input(component_id="type", component_property='value'),
     Input(component_id="months", component_property='value'),
     Input(component_id="mag-slider", component_property='value')]
)
def update_graph(ereignisart, months_slctd, magnitude):
    # erstellen einer kopie der datengrundlage
    quake_df = dff.copy()
    # filter 1: auswahl der ereignisart
    if bool(ereignisart):
        quake_df = quake_df[quake_df['type'].isin(ereignisart)]
    else:
        pass
    # filter 2: filter nach den monaten
    quake_df = quake_df[(quake_df['month'] >= months_slctd[0]) & (quake_df['month'] <= months_slctd[1])]
    # korrektur der datumsspalte
    quake_df['date'] = pd.to_datetime(quake_df['date'])
    # filter 3: magnitudenfilter
    quake_df = quake_df[(quake_df['mag'] >= magnitude[0]) & (quake_df['mag'] <= magnitude[1])]
    # sortierung der daten, damit diese in den plots in der richtigen reihenfolge stehen
    quake_df = quake_df.sort_values('date', ascending=True)
    quake_df = quake_df.sort_values('mag', ascending=True)
    # erstellen des mattrix-df
    matrix_df = quake_df[["depth", "mag", "longitude", "latitude"]]

    # tages-balkendiagramm
    fig2 = px.bar(quake_df,
                  x='date',
                  y='counter',
                  color='mag',
                  labels={
                      "date": "Datum",
                      "counter": "Anzahl",
                      "mag": "Magnitude"
                  })
    # styling barchart
    fig2.update_layout(
        title={
            'text': "Tag der Ereignisse:",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        barmode='stack')

    # weltkarte
    fig = px.scatter_geo(quake_df,
                         lat='latitude',
                         lon='longitude',
                         color='mag',
                         hover_name='date',
                         projection='natural earth',
                         labels={
                             "mag": "Magnitude"})
    # styling map
    fig.update_layout(
        title={
            'text': "Ort der Ereignisse:",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'})

    # tiefen-scatterplot
    fig3 = px.scatter(quake_df,
                      x="mag",
                      y="depth",
                      color="mag",
                      labels={
                          "mag": "Magnitude",
                          "depth": "Tiefe in km"})
    # styling scatterplot
    fig3.update_layout(
        title={
            'text': "Tiefe der Ereignisse:",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'})

    # ereignis-kuchendiagramm
    fig4 = px.pie(quake_df,
                  values='counter',
                  names='type')
    # styling kuchen
    fig4.update_layout(
        title={
            'text': "Art der Ereignisse:",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'})

    # matrix-plot
    fig5 = px.scatter_matrix(matrix_df,
                             labels={
                                 "longitude": "Längengrad",
                                 "latitude": "Breitengrad",
                                 "depth": "Tiefe in km",
                                 "mag": "Magnitude"})

    # styling scatterplots
    fig5.update_traces(diagonal_visible=False)
    fig5.update_layout(
        title={
            'text': "Diverse Scatterplots:",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'})

    return fig, fig2, fig3, fig4, fig5


if __name__ == '__main__':
    app.run_server(debug=False)
