import pandas as pd
import json
from shiny import App, render, ui, reactive
import matplotlib.pyplot as plt
import faicons as fa

with open('database.json', 'r') as json_input:
    json_db = json.load(json_input)
df = pd.DataFrame(json_db["trainList"])

app_ui = ui.page_fluid(
    ui.layout_sidebar(ui.sidebar(
            ui.input_selectize("year", "Select Year", choices=["All"] + sorted(df["Year"].unique().tolist())),
            width=300),
    ui.layout_columns(
        ui.value_box(
            "Number of train taken", ui.output_ui("ntrain"), showcase=fa.icon_svg("train")
        ),
        ui.value_box(
            "Total distance travelled", ui.output_ui("distance"), showcase=fa.icon_svg("route")
        ),
        ui.value_box(
            "Total time in train",
            ui.output_ui("time"),
            showcase=fa.icon_svg("clock", "regular"),
        ),
        fill=False,
    ),
    ui.layout_columns(
        ui.value_box(
            "Average speed", ui.output_ui("speed"), showcase=fa.icon_svg("gauge-high")
        ),
        ui.value_box(
            "Station visited", ui.output_ui("nstation"), showcase=fa.icon_svg("location-dot")
        ),
        ui.value_box(
            "Total delay",
            ui.output_ui("totaldelay"),
            showcase=fa.icon_svg("stopwatch-20"),
        ),
        fill=False,
    ),
    #ui.output_text("meandelay"),
    ui.output_text("mediandelay"),
    ui.output_text("maxdelay"),
    ui.output_text("averagerelative"),
    ui.output_text("medianrelative"),
    ui.output_text("maxrelative"),
    ui.output_plot("traintaken_pl")
))

# Define the server logic
def server(input, output, session):
    @reactive.calc
    def filtered_data():
        if input.year() == "All":
            return df
        else:
            return df[df["Year"] == int(input.year())]

    @output
    @render.text
    def ntrain():
        total = filtered_data().shape[0]
        return total
    
    @output
    @render.text
    def time():
        total = filtered_data()["TravelTime"].sum()
        days = total // (24 * 60)
        hours = (total % (24 * 60)) // 60
        minutes = total % 60
        return f"{days}d, {hours}h & {minutes}mins"
    
    @output
    @render.text
    def totaldelay():
        total = filtered_data()["Delay"].sum()
        days = total // (24 * 60)
        hours = (total % (24 * 60)) // 60
        minutes = total % 60
        return f"{days}d, {hours}h & {minutes}mins"
    
    @output
    @render.text
    def speed():
        total = round(filtered_data()["Distance"].mean(), 2)
        return f"{total} km/h"
    
    @output
    @render.text
    def meandelay():
        total = round(filtered_data()["Delay"].mean(), 2)
        return f"Average delay: {total} min"
    
    @output
    @render.text
    def mediandelay():
        total = filtered_data()["Delay"].median()
        return f"Median delay: {int(total)} min"
    
    @output
    @render.text
    def maxdelay():
        total = filtered_data()["Delay"].max()
        return f"Max delay: {total} min"
    
    @output
    @render.text
    def nstation():
        total = filtered_data()
        unique_values = pd.concat([df['Origin'], df['Destination']]).nunique()
        return unique_values
    
    @output
    @render.text
    def distance():
        total = round(filtered_data()["Distance"].sum(), 2)
        return f"{total} km"

    @output
    @render.text
    def averagerelative():
        total = round(filtered_data()["RelativeDuration"].mean(), 2)
        return f"Average relative duration: {total} %"
    
    @output
    @render.text
    def medianrelative():
        total = filtered_data()["RelativeDuration"].median()
        return f"Mean relative duration: {total} %"
    
    @output
    @render.text
    def maxrelative():
        total = filtered_data()["RelativeDuration"].max()
        return f"Max relative duration: {total} %"
    
    @output
    @render.plot
    def traintaken_pl():
        data = filtered_data()
        
        if input.year() == "All":
            grouped_data = data.groupby(["Year", "Month"]).size().reset_index(name="count")
            grouped_data["year_month"] = grouped_data["Year"].astype(str) + "-" + grouped_data["Month"].astype(str).str.zfill(2)
            x_axis = grouped_data["year_month"]
            title = "Train taken by month"
        else:
            grouped_data = data.groupby("Month").size().reset_index(name="count")
            x_axis = grouped_data["Month"]
            title = "Train taken by month"

        fig, ax = plt.subplots()
        ax.bar(x_axis, grouped_data["count"], color="skyblue")
        ax.set_xlabel("Month")
        ax.set_ylabel("Number of train taken")
        ax.set_title(title)
        plt.xticks(rotation=45)
        plt.tight_layout()

        return fig



app = App(app_ui, server)