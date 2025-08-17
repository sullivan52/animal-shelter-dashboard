from dash import Dash

# Web framework and visualization imports
import dash_leaflet as dl
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import base64
import os
import dash

# Data processing and analysis imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Application modules
from crud import AnimalShelter
from config import RESCUE_CRITERIA, DASHBOARD_CONFIG
from utils import load_animal_data, get_animal_stats, prepare_dashboard_data


def get_friendly_status(outcome_type):
    """
    Convert database outcome codes to user-friendly status descriptions.

    Transforms internal shelter database terminology into language that
    potential adopters can easily understand.

    Args:
        outcome_type (str): Raw outcome type from shelter database

    Returns:
        str: Human-readable status description
    """
    status_mapping = {
        'Adoption': 'Available for Adoption',
        'Transfer': 'Transferred',
        'Return to Owner': 'Returned to Owner',
        'Euthanasia': 'Euthanized',
        'Died': 'Passed Away',
        'Disposal': 'Other Disposal',
        'Rto-Adopt': 'Returned to Owner for Adoption'
    }
    return status_mapping.get(outcome_type, outcome_type)

###########################
# Data Manipulation / Model
###########################
# Import our utilities
from utils import load_animal_data, get_animal_stats, prepare_dashboard_data

# Load real animal data from CSV
df = load_animal_data()

# Prepare data for display
if not df.empty:
    df = prepare_dashboard_data(df)
    stats = get_animal_stats(df)
    print(f"📈 Statistics: {stats}")
else:
    print("❌ No data loaded - check CSV file path")
    stats = {}

#####################################
# Dashboard Layout Configuration
#####################################

# Initialize Dash application
app = Dash(__name__)

# Column mapping for user-friendly table headers
column_mapping = {
    "name": "Name",
    "animal_type": "Animal",
    "breed": "Breed",
    "age_readable": "Age",
    "sex_upon_outcome": "Gender",
    "color": "Color",
    "outcome_type": "Status"
}

columns_to_include = list(column_mapping.keys())

# Configure DataTable columns with display-friendly names
table_columns = [
    {"name": column_mapping[col], "id": col, "deletable": False, "selectable": True}
    for col in columns_to_include
]

# Validate column availability in dataset
if not df.empty:
    available_columns = [col for col in columns_to_include if col in df.columns]
    columns_to_include = available_columns
    print(f"📋 Using columns: {columns_to_include}")

# Main application layout
app.layout = html.Div(
    style={'backgroundColor': '#ffffff', 'color': '#374151', 'padding': '20px'},
    children=[
        # Application header
        html.Center([
            html.H1(
                'Austin Area Animal Adoption Dashboard',
                style={
                    'color': '#059669',
                    'fontSize': '48px',
                    'marginBottom': '30px',
                    'fontWeight': 'bold'
                }
            )
        ]),

        html.Hr(style={'borderColor': '#d1fae5', 'borderWidth': '2px', 'marginBottom': '30px'}),

        # Search and filter controls
        html.Div(
            style={
                'backgroundColor': '#f0fdf4',
                'padding': '25px',
                'borderRadius': '12px',
                'marginBottom': '25px'
            },
            children=[
                html.H4(
                    "Find Your Perfect Companion",
                    style={
                        'color': '#059669',
                        'marginBottom': '25px',
                        'textAlign': 'center',
                        'fontSize': '24px'
                    }
                ),

                # Primary filters: Animal type and breed selection
                html.Div(
                    style={
                        'display': 'flex',
                        'justifyContent': 'center',
                        'gap': '40px',
                        'marginBottom': '25px'
                    },
                    children=[
                        html.Div([
                            html.Label(
                                "Animal Type:",
                                style={
                                    'fontWeight': 'bold',
                                    'color': '#059669',
                                    'marginBottom': '8px',
                                    'display': 'block',
                                    'textAlign': 'center'
                                }
                            ),
                            dcc.Dropdown(
                                id='animal-type-filter',
                                options=[
                                    {'label': 'All Animals', 'value': 'All'},
                                    {'label': 'Dogs', 'value': 'Dog'},
                                    {'label': 'Cats', 'value': 'Cat'},
                                    {'label': 'Other (Rabbits, etc.)', 'value': 'Other'},
                                    {'label': 'Birds', 'value': 'Bird'},
                                    {'label': 'Livestock', 'value': 'Livestock'}
                                ],
                                value='All',
                                style={'width': '280px', 'fontSize': '14px'}
                            )
                        ]),

                        html.Div([
                            html.Label(
                                "Breed:",
                                style={
                                    'fontWeight': 'bold',
                                    'color': '#059669',
                                    'marginBottom': '8px',
                                    'display': 'block',
                                    'textAlign': 'center'
                                }
                            ),
                            dcc.Dropdown(
                                id='breed-filter',
                                options=[{'label': 'All Breeds', 'value': 'All'}],
                                value='All',
                                style={'width': '280px', 'fontSize': '14px'},
                                placeholder="Select a breed...",
                                optionHeight=35
                            )
                        ])
                    ]
                ),

                # Age range selector
                html.Div(
                    style={'marginBottom': '25px', 'maxWidth': '500px', 'margin': '0 auto'},
                    children=[
                        html.Label(
                            "Age Range:",
                            style={
                                'fontWeight': 'bold',
                                'color': '#059669',
                                'marginBottom': '15px',
                                'display': 'block',
                                'textAlign': 'center'
                            }
                        ),
                        dcc.RangeSlider(
                            id='age-range-slider',
                            min=0,
                            max=520,  # 10 years in weeks
                            step=26,  # 6-month intervals
                            marks={
                                0: '0',
                                26: '6mo',
                                52: '1yr',
                                104: '2yr',
                                208: '4yr',
                                312: '6yr',
                                416: '8yr',
                                520: '10yr+'
                            },
                            value=[0, 520],
                            tooltip={"placement": "bottom", "always_visible": False}
                        )
                    ]
                ),

                # Quick filter buttons and reset controls
                html.Div(style={'textAlign': 'center'}, children=[
                    html.Label(
                        "Quick Filters:",
                        style={
                            'fontWeight': 'bold',
                            'color': '#059669',
                            'marginBottom': '15px',
                            'display': 'block'
                        }
                    ),

                    # Preset filter buttons
                    html.Div(
                        style={
                            'display': 'flex',
                            'justifyContent': 'center',
                            'gap': '15px',
                            'flexWrap': 'wrap',
                            'marginBottom': '15px'
                        },
                        children=[
                            html.Button(
                                "Puppies/Kittens",
                                id='btn-young',
                                n_clicks=0,
                                style={
                                    'backgroundColor': '#10b981',
                                    'color': 'white',
                                    'border': 'none',
                                    'padding': '10px 20px',
                                    'borderRadius': '8px',
                                    'cursor': 'pointer',
                                    'fontSize': '14px',
                                    'fontWeight': '500'
                                }
                            ),
                            html.Button(
                                "Adult Animals",
                                id='btn-adult',
                                n_clicks=0,
                                style={
                                    'backgroundColor': '#10b981',
                                    'color': 'white',
                                    'border': 'none',
                                    'padding': '10px 20px',
                                    'borderRadius': '8px',
                                    'cursor': 'pointer',
                                    'fontSize': '14px',
                                    'fontWeight': '500'
                                }
                            ),
                            html.Button(
                                "Senior Animals",
                                id='btn-senior',
                                n_clicks=0,
                                style={
                                    'backgroundColor': '#10b981',
                                    'color': 'white',
                                    'border': 'none',
                                    'padding': '10px 20px',
                                    'borderRadius': '8px',
                                    'cursor': 'pointer',
                                    'fontSize': '14px',
                                    'fontWeight': '500'
                                }
                            ),
                            html.Button(
                                "Available Now",
                                id='btn-available',
                                n_clicks=0,
                                style={
                                    'backgroundColor': '#059669',
                                    'color': 'white',
                                    'border': 'none',
                                    'padding': '10px 20px',
                                    'borderRadius': '8px',
                                    'cursor': 'pointer',
                                    'fontSize': '14px',
                                    'fontWeight': '500'
                                }
                            ),
                        ]
                    ),

                    # Reset all filters button
                    html.Button(
                        "🔄 Reset All Filters",
                        id='btn-reset',
                        n_clicks=0,
                        style={
                            'backgroundColor': '#dc2626',
                            'color': 'white',
                            'border': 'none',
                            'padding': '6px 16px',
                            'borderRadius': '6px',
                            'cursor': 'pointer',
                            'fontSize': '12px',
                            'fontWeight': '500'
                        }
                    )
                ])
            ]
        ),

        html.Hr(style={'borderColor': '#d1fae5'}),

        # Animal data table
        dash_table.DataTable(
            id='datatable-id',
            columns=table_columns,
            data=df[columns_to_include].to_dict('records') if not df.empty and len(columns_to_include) > 0 else [],
            row_selectable="single",
            selected_rows=[0] if not df.empty else [],
            page_size=10,
            filter_action="native",  # Enable column-level filtering
            sort_action="native",  # Enable column sorting
            sort_mode="multi",  # Allow multi-column sorting
            style_table={
                'overflowX': 'auto',
                'backgroundColor': '#ffffff',
                'borderRadius': '8px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
            },
            style_data={
                'backgroundColor': '#ffffff',
                'color': '#374151',
                'border': '1px solid #e5e7eb'
            },
            style_data_conditional=[
                {'if': {'row_index': 'odd'}, 'backgroundColor': '#f9fafb'},
                {'if': {'state': 'selected'}, 'backgroundColor': '#d1fae5', 'color': '#065f46', 'fontWeight': 'bold'}
            ],
            style_header={
                'fontWeight': 'bold',
                'textAlign': 'center',
                'backgroundColor': '#059669',
                'color': 'white',
                'border': '1px solid #047857'
            },
            style_cell={
                'whiteSpace': 'normal',
                'height': 'auto',
                'minWidth': '100px',
                'width': '150px',
                'maxWidth': '200px',
                'textAlign': 'left',
                'padding': '12px',
                'fontFamily': '"Segoe UI", "Roboto", "Helvetica Neue", Arial, sans-serif',
                'fontSize': '14px'
            }
        ),

        html.Br(),
        html.Hr(style={'borderColor': '#d1fae5'}),

        # Interactive map section
        html.Div([
            # Map toggle controls
            html.Div(
                style={'textAlign': 'center', 'marginBottom': '20px'},
                children=[
                    html.Button(
                        "📍 Show Animals on Map",
                        id='toggle-map-btn',
                        n_clicks=0,
                        style={
                            'backgroundColor': '#059669',
                            'color': 'white',
                            'border': 'none',
                            'padding': '12px 24px',
                            'borderRadius': '8px',
                            'fontSize': '16px',
                            'fontWeight': 'bold',
                            'cursor': 'pointer',
                            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                        }
                    ),
                    html.Div(id='map-info', style={'marginTop': '10px', 'color': '#6b7280'})
                ]
            ),

            # Map display container
            html.Div(
                id='map-id',
                style={
                    'backgroundColor': '#f9fafb',
                    'borderRadius': '8px',
                    'padding': '20px',
                    'minHeight': '500px'
                }
            )
        ])
    ]
)


#####################################
# Interactive Dashboard Callbacks
#####################################

@app.callback(
    Output('datatable-id', 'style_data_conditional'),
    [Input('datatable-id', 'selected_columns')]
)
def update_table_styles(selected_columns):
    """
    Apply conditional styling to selected table columns.

    Args:
        selected_columns (list): List of column IDs that are currently selected

    Returns:
        list: Styling rules for DataTable conditional formatting
    """
    if not selected_columns:
        return []

    return [{
        'if': {'column_id': column_id},
        'background_color': '#D2F3FF'
    } for column_id in selected_columns]


@app.callback(
    [Output('datatable-id', 'data'),
     Output('animal-type-filter', 'value'),
     Output('breed-filter', 'value'),
     Output('breed-filter', 'options'),
     Output('age-range-slider', 'value')],
    [Input('animal-type-filter', 'value'),
     Input('breed-filter', 'value'),
     Input('age-range-slider', 'value'),
     Input('btn-young', 'n_clicks'),
     Input('btn-adult', 'n_clicks'),
     Input('btn-senior', 'n_clicks'),
     Input('btn-available', 'n_clicks'),
     Input('btn-reset', 'n_clicks')]
)
def update_dashboard_filters(animal_type, selected_breed, age_range, btn_young, btn_adult,
                             btn_senior, btn_available, btn_reset):
    """
    Central controller for all dashboard filtering operations.

    Handles filter interactions, data processing, and UI state management.
    Manages dynamic breed dropdown population based on animal type selection.

    Args:
        animal_type (str): Selected animal type filter value
        selected_breed (str): Selected breed filter value
        age_range (list): Min/max age range in weeks [min, max]
        btn_young (int): Number of clicks on young animals button
        btn_adult (int): Number of clicks on adult animals button
        btn_senior (int): Number of clicks on senior animals button
        btn_available (int): Number of clicks on available animals button
        btn_reset (int): Number of clicks on reset button

    Returns:
        tuple: (filtered_data, animal_type_value, breed_value, breed_options, age_range_value)
    """
    try:
        # Initialize with complete dataset
        df_filtered = df.copy()

        # Identify which control triggered the callback
        ctx = dash.callback_context
        button_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

        # Handle reset functionality - restore all defaults
        if button_id == 'btn-reset':
            all_breeds = sorted(df['breed'].dropna().unique())
            breed_options = [{'label': 'All Breeds', 'value': 'All'}]
            breed_options.extend([{'label': breed, 'value': breed} for breed in all_breeds])
            return df.to_dict('records'), 'All', 'All', breed_options, [0, 520]

        # Update breed dropdown options based on selected animal type
        if animal_type == 'All':
            available_breeds = sorted(df['breed'].dropna().unique())
        else:
            filtered_breeds = df[df['animal_type'] == animal_type]['breed'].dropna().unique()
            available_breeds = sorted(filtered_breeds)

        breed_options = [{'label': 'All Breeds', 'value': 'All'}]
        breed_options.extend([{'label': breed, 'value': breed} for breed in available_breeds])

        # Reset breed selection when animal type changes
        if button_id == 'animal-type-filter':
            selected_breed = 'All'

        # Process quick filter button selections
        # Each button applies specific age-based filters and resets other selections
        if button_id == 'btn-young':
            df_filtered = df_filtered[df_filtered['age_upon_outcome_in_weeks'] <= 52]  # 1 year or younger
            animal_type = 'All'
            selected_breed = 'All'
        elif button_id == 'btn-adult':
            df_filtered = df_filtered[
                (df_filtered['age_upon_outcome_in_weeks'] > 52) &
                (df_filtered['age_upon_outcome_in_weeks'] <= 312)  # 1-6 years
                ]
            animal_type = 'All'
            selected_breed = 'All'
        elif button_id == 'btn-senior':
            df_filtered = df_filtered[df_filtered['age_upon_outcome_in_weeks'] > 312]  # 6+ years
            animal_type = 'All'
            selected_breed = 'All'
        elif button_id == 'btn-available':
            df_filtered = df_filtered[df_filtered['outcome_type'] == 'Adoption']
            animal_type = 'All'
            selected_breed = 'All'

        # Apply individual filter criteria
        # Animal type filter
        if animal_type and animal_type != 'All':
            df_filtered = df_filtered[df_filtered['animal_type'] == animal_type]

        # Breed filter
        if selected_breed and selected_breed != 'All':
            df_filtered = df_filtered[df_filtered['breed'] == selected_breed]

        # Age range filter (skip if quick filter button was used)
        if age_range and button_id not in ['btn-young', 'btn-adult', 'btn-senior']:
            min_age, max_age = age_range
            df_filtered = df_filtered[
                (df_filtered['age_upon_outcome_in_weeks'] >= min_age) &
                (df_filtered['age_upon_outcome_in_weeks'] <= max_age)
                ]

        print(f"🔍 Filtered to {len(df_filtered)} animals")
        return df_filtered.to_dict('records'), animal_type, selected_breed, breed_options, age_range

    except Exception as e:
        print(f"❌ Error in dashboard filtering: {e}")
        # Return safe defaults on error
        all_breeds = sorted(df['breed'].dropna().unique())
        breed_options = [{'label': 'All Breeds', 'value': 'All'}]
        breed_options.extend([{'label': breed, 'value': breed} for breed in all_breeds])
        return df.to_dict('records') if not df.empty else [], 'All', 'All', breed_options, [0, 520]


@app.callback(
    [Output('map-id', "children"),
     Output('toggle-map-btn', 'children'),
     Output('map-info', 'children')],
    [Input('toggle-map-btn', 'n_clicks'),
     Input('datatable-id', "derived_virtual_data")]
)
def update_interactive_map(n_clicks, filtered_data):
    """
    Manage interactive map display and animal location markers.

    Controls map visibility, generates location markers for filtered animals,
    and provides performance optimization through marker limiting.

    Args:
        n_clicks (int): Number of times the map toggle button has been clicked
        filtered_data (list): Current filtered animal data from the table

    Returns:
        tuple: (map_content, button_text, info_message)
    """
    # Toggle map visibility based on button clicks (even = hidden, odd = shown)
    map_is_hidden = (n_clicks % 2 == 0)

    # Display instructions when map is hidden
    if map_is_hidden:
        return [
            html.Div(
                "Click the button above to view animals on an interactive map",
                style={'color': '#6b7280', 'textAlign': 'center', 'fontSize': '18px', 'padding': '50px'}
            ),
            "📍 Show Animals on Map",
            ""
        ]

    # Handle case where no data is available for mapping
    if not filtered_data:
        return [
            html.Div(
                "Use the filters above to select animals, then the map will show their locations.",
                style={'color': '#6b7280', 'textAlign': 'center', 'fontSize': '16px', 'padding': '50px'}
            ),
            "🗺️ Hide Map",
            "Select some filters to see animals on the map"
        ]

    # Convert filtered data to DataFrame for processing
    animal_data = pd.DataFrame.from_dict(filtered_data)

    # Implement performance optimization - limit markers to prevent browser slowdown
    if len(animal_data) > 100:
        map_data = animal_data.head(100)
        info_message = f"Showing first 100 of {len(animal_data)} animals on map. Use filters to narrow results."
    else:
        map_data = animal_data
        info_message = f"Showing all {len(animal_data)} animals on map."

    # Generate map markers for each animal with valid coordinates
    markers = []
    for _, animal in map_data.iterrows():
        if pd.notna(animal.get('location_lat')) and pd.notna(animal.get('location_long')):
            latitude, longitude = animal['location_lat'], animal['location_long']

            # Create interactive marker with tooltip and detailed popup
            markers.append(
                dl.Marker(
                    position=[latitude, longitude],
                    children=[
                        dl.Tooltip(
                            f"{animal.get('name', 'Unknown')} - {animal.get('breed', 'Unknown breed')}"
                        ),
                        dl.Popup([
                            html.Div([
                                html.H2(
                                    animal.get('name', 'Unknown Animal'),
                                    style={'color': '#059669', 'marginBottom': '10px'}
                                ),
                                html.P(
                                    f"🐾 {animal.get('animal_type', 'Unknown')} • {animal.get('breed', 'Unknown breed')}",
                                    style={'fontSize': '16px', 'fontWeight': 'bold', 'marginBottom': '8px'}
                                ),
                                html.P(
                                    f"🎂 {animal.get('age_readable', 'Unknown age')}",
                                    style={'marginBottom': '5px'}
                                ),
                                html.P(
                                    f"⚧ {animal.get('sex_upon_outcome', 'Unknown gender')}",
                                    style={'marginBottom': '5px'}
                                ),
                                html.P(
                                    f"🎨 {animal.get('color', 'Unknown color')}",
                                    style={'marginBottom': '5px'}
                                ),
                                html.P(
                                    f"📋 Status: {get_friendly_status(animal.get('outcome_type', 'Unknown status'))}",
                                    style={'marginBottom': '10px', 'fontWeight': 'bold'}
                                ),
                            ], style={'padding': '15px', 'fontFamily': '"Segoe UI", Roboto, sans-serif'})
                        ], maxWidth=300)
                    ]
                )
            )

    # Calculate map center point (use first animal's location or default to Austin)
    center_latitude = map_data.iloc[0]['location_lat'] if not map_data.empty else 30.75
    center_longitude = map_data.iloc[0]['location_long'] if not map_data.empty else -97.48

    # Return complete map component
    return [
        dl.Map(
            style={'width': '100%', 'height': '600px'},
            center=[center_latitude, center_longitude],
            zoom=10,
            children=[dl.TileLayer(id="base-layer-id"), *markers]
        ),
        "🗺️ Hide Map",
        info_message
    ]


###########################
# Application Entry Point
###########################

if __name__ == '__main__':
    app.run(debug=DASHBOARD_CONFIG['debug'])

