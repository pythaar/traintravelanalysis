import pandas as pd
import json
from shiny import App, render, ui, reactive

with open('database.json', 'r') as json_input:
    json_db = json.load(json_input)
df = pd.DataFrame(json_db["trainList"])


"""
delay_mean = df['Delay'].mean()
delay_median = df['Delay'].median()
price_total = df['Price'].sum()
distance_total = df['Distance'].sum()
speed_mean = df['Speed'].mean()
traveltime_total = df['TravelTime'].sum()

app_ui = ui.page_fluid(
    ui.input_select("filter_by", "Filtrer par", ["Origine", "Destination", "Type"]),
    ui.output_text("delay_mean"),
    ui.output_text("delay_median"),
    ui.output_text("price_total"),
    ui.output_text("distance_total"),
    ui.output_text("speed_mean"),
    ui.output_text("traveltime_total")
)

def server(input, output, session):
    @output
    @render.text
    def delay_mean():
        filtered_df = df[df[input.filter_by] == input.filter_value]
        return f"Delay moyen: {filtered_df['Delay'].mean()}"

    @output
    @render.text
    def delay_median():
        filtered_df = df[df[input.filter_by] == input.filter_value]
        return f"Delay médian: {filtered_df['Delay'].median()}"

    @output
    @render.text
    def price_total():
        filtered_df = df[df[input.filter_by] == input.filter_value]
        return f"Price total: {filtered_df['Price'].sum()}"

    @output
    @render.text
    def distance_total():
        filtered_df = df[df[input.filter_by] == input.filter_value]
        return f"Distance totale: {filtered_df['Distance'].sum()}"

    @output
    @render.text
    def speed_mean():
        filtered_df = df[df[input.filter_by] == input.filter_value]
        return f"Speed moyenne: {filtered_df['Speed'].mean()}"

    @output
    @render.text
    def traveltime_total():
        filtered_df = df[df[input.filter_by] == input.filter_value]
        return f"TravelTime total: {filtered_df['TravelTime'].sum()}"

"""
app_ui = ui.page_fluid(
    ui.input_selectize("year", "Select Year", choices=["All"] + sorted(df["Year"].unique().tolist())),
    ui.output_text("ntrain"),
    ui.output_text("distance"),
    ui.output_text("time"),
    ui.output_text("speed"),
    ui.output_text("totaldelay"),
    ui.output_text("meandelay"),
    ui.output_text("mediandelay")
)

# Define the server logic
def server(input, output, session):
    @reactive.calc
    def filtered_data():
        if input.year() == "All":
            return df
        else:
            return df[df["Year"] == input.year()]

    @output
    @render.text
    def ntrain():
        total = filtered_data().shape[0]
        return f"Total train taken: {total}"
    
    @output
    @render.text
    def time():
        total = filtered_data()["TravelTime"].sum()
        days = total // (24 * 60)
        hours = (total % (24 * 60)) // 60
        minutes = total % 60
        return f"Total time travelled: {days} days, {hours} hours and {minutes} minutes"
    
    @output
    @render.text
    def totaldelay():
        total = filtered_data()["Delay"].sum()
        days = total // (24 * 60)
        hours = (total % (24 * 60)) // 60
        minutes = total % 60
        return f"Total delay: {days} days, {hours} hours and {minutes} minutes"
    
    @output
    @render.text
    def speed():
        total = round(filtered_data()["Distance"].mean(), 2)
        return f"Average speed: {total} km/h"
    
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
    def distance():
        total = round(filtered_data()["Distance"].sum(), 2)
        return f"Distance travelled: {total} km"



app = App(app_ui, server)