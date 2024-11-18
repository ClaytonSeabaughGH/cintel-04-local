import plotly.express as px
import plotly.graph_objects as go
from shiny.express import ui, render
from shinywidgets import render_plotly, output_widget
import palmerpenguins
import seaborn as sns
import matplotlib.pyplot as plt
from shiny import reactive, Inputs, ui, App
import pandas as pd

# Load data
penguins_df = palmerpenguins.load_penguins()

# --------------------------------------------------------
# Define User Interface
# --------------------------------------------------------

app_ui = ui.page_fluid(
    ui.panel_title("Clayton's Penguin Data"),
    ui.layout_sidebar(
        # Wrap the sidebar elements within `ui.sidebar()`
        ui.sidebar(
            ui.h2("Sidebar"),
            ui.input_selectize(
                "selected_attribute",
                "Select an attribute",
                ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"],
            ),
            ui.input_numeric("plotly_bin_count", "Plotly Bin Count", 20),
            ui.input_slider("seaborn_bin_count", "Seaborn Bin Count", 1, 20, 10),
            # Checkbox group for filtering species
            ui.input_checkbox_group(
                "selected_species_list",
                "Filter by Species",
                ["Adelie", "Gentoo", "Chinstrap"],
                selected=["Adelie", "Gentoo", "Chinstrap"],
            ),
            # Checkbox group for filtering the dataset by penguin island
            ui.input_checkbox_group(
                "selected_island_list",
                "Filter by Island:",
                ["Biscoe", "Dream", "Torgersen"],
                selected=["Biscoe", "Dream", "Torgersen"],
            ),
            ui.input_slider("body_mass_range", "Filter by Body Mass (g)", 1000, 6000, [2000, 5000]),
            ui.hr(),
            ui.a(
                "GitHub",
                href="https://github.com/ClaytonSeabaughGH/cintel-02-data",
                target="_blank",
            ),
        ),
        # Main content
        ui.panel_fixed(
            ui.layout_columns(
                # Penguins Data Table
                ui.card(
                    "Penguins Data Table",
                    ui.output_data_frame("penguins_table")
                ),
                # Penguins Data Grid
                ui.card(
                    "Penguins Data Grid",
                    ui.output_data_frame("penguins_grid")
                )
            ),
            ui.layout_columns(
                # Plotly Histogram
                ui.card(
                    "Plotly Histogram",
                    ui.output_plot("plotly_histogram")
                ),
                # Seaborn Histogram
                ui.card(
                    "Seaborn Histogram",
                    ui.output_plot("seaborn_histogram")
                ),
            ),
            ui.layout_columns(
                # Plotly Scatterplot
                ui.card(
                    "Plotly Scatterplot",
                    ui.output_plot("plotly_scatterplot")
                ),
                # Plotly Violin Plot
                ui.card(
                    "Plotly Violin Plot",
                    ui.output_plot("plotly_violin")
                )
            ),
        )
    )
)

# --------------------------------------------------------
# Server Logic
# --------------------------------------------------------

def server(input: Inputs, output, session):
    # Define a reactive calculation for data filtering
    @reactive.Calc
    def filtered_data() -> pd.DataFrame:
        filtered_df = penguins_df[
            penguins_df["species"].isin(input.selected_species_list())
        ]
        filtered_df = filtered_df[filtered_df["island"].isin(input.selected_island_list())]
        mass_min, mass_max = input.body_mass_range()
        filtered_df = filtered_df[
            (filtered_df["body_mass_g"] >= mass_min) & 
            (filtered_df["body_mass_g"] <= mass_max)
        ]
        return filtered_df

    # Penguins Data Table
    @output
    @render.data_frame
    def penguins_table():
        return filtered_data()

    # Penguins Data Grid
    @output
    @render.data_frame
    def penguins_grid():
        return filtered_data()

    # Plotly Histogram
    @output
    @render_plotly
    def plotly_histogram():
        selected_attribute = input.selected_attribute()
        bin_count = input.plotly_bin_count()
        filtered_df = filtered_data()
        fig = px.histogram(
            filtered_df,
            x=selected_attribute,
            nbins=bin_count,
            title=f"Histogram of {selected_attribute}",
            color="species"
        )
        fig.update_traces(marker_line_color="black", marker_line_width=1)
        return fig

    # Seaborn Histogram
    @output
    @render.plot
    def seaborn_histogram():
        selected_attribute = input.selected_attribute()
        filtered_df = filtered_data()
        ax = sns.histplot(
            data=filtered_df,
            x=selected_attribute,
            bins=input.seaborn_bin_count(),
            hue="species",
            multiple="stack"
        )
        ax.set_title("Seaborn Histogram")
        ax.set_xlabel(selected_attribute)
        ax.set_ylabel("Count")
        return ax

    # Plotly Scatterplot
    @output
    @render_plotly
    def plotly_scatterplot():
        filtered_df = filtered_data()
        fig = px.scatter(
            filtered_df,
            x="body_mass_g",
            y="flipper_length_mm",
            color="species",
            title="Scatterplot: Body Mass vs Flipper Length",
            labels={"body_mass_g": "Body Mass (g)", "flipper_length_mm": "Flipper Length (mm)"}
        )
        return fig

    # Plotly Violin Plot
    @output
    @render_plotly
    def plotly_violin():
        selected_attribute = input.selected_attribute()
        filtered_df = filtered_data()
        fig = px.violin(
            filtered_df,
            y=selected_attribute,
            x="species",
            box=True,
            points="all",
            title=f"Violin Plot of {selected_attribute} by Species",
            color="species"
        )
        return fig

app = App(ui=app_ui, server=server)

if __name__ == "__main__":
    app.run()

