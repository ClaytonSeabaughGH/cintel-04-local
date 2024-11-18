import plotly.express as px
from shiny.express import ui, render, input
from shinywidgets import render_plotly, render_widget
import palmerpenguins
import seaborn as sns
import matplotlib.pyplot as plt
from shiny import reactive
import pandas as pd

# Load data
penguins_df = palmerpenguins.load_penguins()


# -----------------------
# Define User Interface
# ------------------------

# Add a sidebar
with ui.sidebar(open="open"):
    ui.h2("Sidebar")
    
    # Drop-Down menu
    ui.input_selectize(
        id="selected_attribute",
        label="Selected Attribute",
        choices=["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"],
    )
    

    ui.input_numeric("plotly_bin_count", "Plotly Bin Count", 20)

    ui.input_slider("seaborn_bin_count", "Seaborn Bin Count", 1, 20, 10)

    # Checkbox group for filtering species
    ui.input_checkbox_group(
        "selected_species_list",
        "Filter by Species",
        ["Adelie", "Gentoo", "Chinstrap"],
        selected=["Adelie", "Gentoo", "Chinstrap"],
        inline=False,
    )
    # Checkbox group for filtering the dataset by penguin island
    ui.input_checkbox_group(
        "selected_island_list",
        "Filter by Island:",
        ["Biscoe", "Dream", "Torgersen"],
        selected=["Biscoe", "Dream", "Torgersen"],
        inline=False,
    )
    # Add numeric range filter for Body Mass
    ui.input_slider("body_mass_range", "Filter by Body Mass", 1000, 6000, [2000, 5000])

   
    ui.hr()
    ui.a(
        "GitHub",
        href="https://github.com/ClaytonSeabaughGH/cintel-02-data",
        target="_blank",
    )
    


# ----------------------------------------
# Create Main layout for displaying plots
# ----------------------------------------

ui.page_opts(title="Clayton's Penguin Data", fillable=True)

#-------------------------------
# Create Data gird and table
#-------------------------------
with ui.layout_columns():
    # Create Data Table
    with ui.card():
        "Penguins Data Table"

        @render.data_frame
        def penguinstable_df():
            return render.DataTable(penguins_df, filters=False, selection_mode="row")

    # Create Data Grid
    with ui.card():
        "Penguins Data Grid"

        @render.data_frame
        def penguinsgrid_df():
            return render.DataGrid(penguins_df, filters=False, selection_mode="row")
        
#-----------------------------
# Create Plots
#----------------------------

# Create interactive plotly plot
with ui.layout_columns(col_widths=6):
    with ui.card(full_screen=True):
    # Add a title with dynamic information
        @render_widget
        def plotly_plot():
            filtered_df = filtered_data()
            selected_attribute = input.selected_attribute()
            bin_count = input.plotly_bin_count()
            species_filter = ', '.join(input.selected_species_list())
            fig = px.histogram(
                filtered_df,
                x=selected_attribute,
                nbins=bin_count,
                title=f"Plotly Histogram: {selected_attribute} (Species: {species_filter})",
                color="species",
    )
            fig.update_traces(marker_line_color="black", marker_line_width=2)
            fig.update_layout(width=800)
            return fig

# Create interactive seaborn plot
    with ui.card(full_screen=True):
        
        @render.plot(alt="Seaborn Histogram")
        def seaborn_plot():
            selected_attribute = input.selected_attribute()
            filtered_df = filtered_data()
            ax = sns.histplot(
                data=filtered_df,
                x=selected_attribute,
                bins=input.seaborn_bin_count(),
                hue="species",
                multiple="stack",
            )
            ax.set_title("Seaborn Histogram")
            ax.set_xlabel(selected_attribute)
            ax.set_ylabel("Count")
            return ax

# Create plotly scatter plot
    with ui.card():
        ui.card_header("Plotly Scatterplot: Species")

        @render_widget
        def plotly_scatterplot():
            filtered_df = filtered_data()
            fig = px.scatter(
                filtered_df,
                x="body_mass_g",
                y="flipper_length_mm",
                color="species",
                title="Penguins Scatterplot: Body Mass vs. Flipper Length",
                labels={
                "body_mass_g": "Body Mass (g)",
                "flipper_length_mm": "Flipper Length (mm)",
            },
        )
            return fig

# Create a violin plot showing distribution of mass
    with ui.card():
        ui.card_header("Plotly Violinplot: Species")

        @render_plotly
        def line_plot():
            filtered_df = filtered_data()
            selected_attribute = input.selected_attribute()
            fig = px.violin(
                filtered_df,
                y=selected_attribute,
                x="species",
                box=True,
                points="all",
                title="Attribute Distribution by Species",
                color="species",
        )
            return fig

# --------------------------------------------------------
# Reactive calculations and effects
# --------------------------------------------------------

# Define a reactive calculation for data filtering

@reactive.calc
def filtered_data() -> pd.DataFrame:
    # Apply species filter
    filtered_df = penguins_df[
        penguins_df["species"].isin(input.selected_species_list())
    ]
    
    # Apply island filter
    filtered_df = filtered_df[filtered_df["island"].isin(input.selected_island_list())]
    
    # Add filter for body mass
    mass_min, mass_max = input.body_mass_range()
    filtered_df = filtered_df[(filtered_df['body_mass_g'] >= mass_min) & (filtered_df['body_mass_g'] <= mass_max)]

    # Check if the DataFrame is empty after applying all filters
    if filtered_df.empty:
        return pd.DataFrame()  # Return an empty DataFrame if no data matches the filters

    return filtered_df
