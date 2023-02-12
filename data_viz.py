from dash import Dash, dcc, Output, Input,html,dash_table
import dash_bootstrap_components as dbc 
import plotly.express as px
import pandas as pd
from pymongo import MongoClient
from config import password

"""setting up the mongodb database using pymongo"""
client= MongoClient(f"mongodb+srv://Harshan:{password}@firstcluster.zxdpy3p.mongodb.net/?retryWrites=true&w=majority")
db=client["B_C_pymongo"]
collection=db["task-3"]

df = pd.DataFrame(list(collection.find({})))[:300]
df=df[["intensity","country","end_year","topic","impact","relevance","likelihood","sector"]]
print(df.columns)

# -------------------------------------------------------------------------------------
# App layout
app = Dash(__name__, prevent_initial_callbacks=True,external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([dbc.Row(dbc.Col(html.H1("DATA VISUALIZATION DASHBOARD"),width={"size":5.5},style={"color":"red","background-color":"black","text-align":"center"})),
    dash_table.DataTable(
        id='datatable-interactivity',
        columns=[
            {"name": i, "id": i, "deletable": True, "selectable": True, "hideable": True}
            if i == "intensity" or i == "end_year" or i == "sector"
            else {"name": i, "id": i, "deletable": True, "selectable": True}
            for i in df.columns ],
        data=df.to_dict('records'),  # the contents of the table
        editable=True,              # allow editing of data inside all cells
        filter_action="native",     # allow filtering of data by user ('native') or not ('none')
        sort_action="native",       # enables data to be sorted per-column by user or not ('none')
        sort_mode="single",         # sort across 'multi' or 'single' columns
        column_selectable="multi",  # allow users to select 'multi' or 'single' columns
        row_selectable="multi",     # allow users to select 'multi' or 'single' rows
        row_deletable=True,         # choose if user can delete a row (True) or not (False)
        selected_columns=[],        # ids of columns that user selects
        selected_rows=[],           # indices of rows that user selects
        page_action="native",       # all data is passed to the table up-front or not ('none')
        page_current=0,             # page number that user is on
        page_size=6,                # number of rows visible per page
        style_cell={                # ensure adequate header width when text is shorter than cell's text
            'minWidth': 95, 'maxWidth': 95, 'width': 95
        },
        style_cell_conditional=[    # align text columns to left. By default they are aligned to right
            {
                'if': {'column_id': c},
                'textAlign': 'left'
            } for c in ['country']
        ],
        style_data={                # overflow cells' content into multiple lines
            'whiteSpace': 'normal',
            'height': 'auto'
        }
    ),

    html.Br(),
    html.Br(),
    html.Div(id='bar-container'),
    html.Div(id='choromap-container'),
    html.Div(id='pie-container')

])

# -------------------------------------------------------------------------------------
# Create bar chart
@app.callback(
    Output(component_id='bar-container', component_property='children'),
    [Input(component_id='datatable-interactivity', component_property="derived_virtual_data"),
     Input(component_id='datatable-interactivity', component_property='derived_virtual_selected_rows'),
     Input(component_id='datatable-interactivity', component_property='derived_virtual_selected_row_ids'),
     Input(component_id='datatable-interactivity', component_property='selected_rows'),
     Input(component_id='datatable-interactivity', component_property='derived_virtual_indices'),
     Input(component_id='datatable-interactivity', component_property='derived_virtual_row_ids'),
     Input(component_id='datatable-interactivity', component_property='active_cell'),
     Input(component_id='datatable-interactivity', component_property='selected_cells')]
)
def update_scatter(all_rows_data, slctd_row_indices, slct_rows_names, slctd_rows,
               order_of_rows_indices, order_of_rows_names, actv_cell, slctd_cell):
    dff = pd.DataFrame(all_rows_data)

    # used to highlight selected countries on bar chart
    colors = ['#FF0000' if i in slctd_row_indices else '#0074D9'
              for i in range(len(dff))]

    if "sector" in dff and "topic" in dff:
        return [
            dcc.Graph(id='scatter-chart',
                      figure=px.scatter(
                          data_frame=dff,
                          x="country",
                          y='sector',
                          labels={"Different sectors in the various countries"}
                      ).update_layout(showlegend=False, xaxis={'categoryorder': 'total ascending'})
                      .update_traces(marker_color=colors, hovertemplate="<b>%{y}%</b><extra></extra>")
                      )
        ]

# Create choropleth map
@app.callback(
    Output(component_id='choromap-container', component_property='children'),
    [Input(component_id='datatable-interactivity', component_property="derived_virtual_data"),
     Input(component_id='datatable-interactivity', component_property='derived_virtual_selected_rows')]
)
def update_map(all_rows_data, slctd_row_indices):
    dff = pd.DataFrame(all_rows_data)

    # highlight selected countries on map
    borders = [5 if i in slctd_row_indices else 1
               for i in range(len(dff))]

    if "country" in dff and "sector" in dff and "intensity" in dff:
        return [
            dcc.Graph(id='choropleth',
                      style={'height': 700},
                      figure=px.choropleth(
                          data_frame=dff,
                          locations="country",
                          scope="world",
                          color="intensity",
                          title="Different sectors in the countries",
                          template='plotly_dark',
                          hover_data=['country', 'intensity'],
                      ).update_layout(showlegend=False, title=dict(font=dict(size=28), x=0.5, xanchor='center'))
                      .update_traces(marker_line_width=borders, hovertemplate="<b>%{customdata[0]}</b><br><br>" +
                                                                              "%{customdata[1]}" + "%")
                      )
        ]

# Highlight selected column
@app.callback(
    Output('datatable-interactivity', 'style_data_conditional'),
    [Input('datatable-interactivity', 'selected_columns')]
)
def update_styles(selected_columns):
    return [{
        'if': {'column_id': i},
        'background_color': '#D2F3FF'
    } for i in selected_columns]


def pie():
    px.pie(data_frame=df, names='country', title='Count of topics')

if __name__ == '__main__':
    app.run_server(debug=True)
    