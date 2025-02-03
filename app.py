import pandas as pd
import json
from shiny import App, render, ui, reactive
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import faicons as fa
import numpy as np

#---------------- TO DO ---------------#
#ADD 2 colonnes, une pour chaque, en donnant l'axe sur lequel ça s'est produit (Genre Lille-Aulnoye)
#Utiliser des check box au lieu des selectize
#Voir comment update auto le df pour la selection des données

with open('database.json', 'r') as json_input:
    json_db = json.load(json_input)
init_df = pd.DataFrame(json_db["trainList"])

app_ui = ui.page_fluid(
    ui.layout_sidebar(ui.sidebar(
            ui.input_selectize("year", "Select Year", choices=["All"] + sorted(init_df["Year"].unique().tolist())),
            ui.input_selectize("type", "Select Train type", choices=["All"] + sorted(init_df["Type"].unique().tolist())),
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
    ui.output_plot("table"),
    ui.layout_columns(ui.output_plot("traintaken_pl"),
    ui.output_plot("piedelay"))
))

# Define the server logic
def server(input, output, session):
    @reactive.calc
    def filtered_data():
        with open('database.json', 'r') as json_input:
            json_db = json.load(json_input)
        df = pd.DataFrame(json_db["trainList"])
        if input.year() != "All":
            df =  df[df["Year"] == int(input.year())]
        
        if input.type() == "All":
            return df
        else:
            return df[df["Type"] == input.type()]

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
        total = round(filtered_data()["Speed"].mean(), 2)
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
        unique_values = pd.concat([total['Origin'], total['Destination']]).nunique()
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
        else:
            grouped_data = data.groupby("Month").size().reset_index(name="count")
            x_axis = grouped_data["Month"]
            
        title = "Train taken by month"
        fig, ax = plt.subplots()
        ax.plot(x_axis, grouped_data["count"], color="skyblue")
        ax.set_xlabel("Month")
        ax.set_ylabel("Number of train taken")
        ax.set_title(title)
        plt.xticks(rotation=45)
        plt.tight_layout()

        return fig
    
    @output
    @render.plot
    def piedelay():
        df = filtered_data()
        
        bins = [-float('inf'), -1, 1, 5, 10, 30, float('inf')]
        labels = ['Early', 'On time', 'Low delay (<5 min)', 
                'Delay (between 5 and 10)', 'Big delay (between 10 and 30)', 'Very big delay (>30 min)']

        df['Catégorie'] = pd.cut(df['Delay'], bins=bins, labels=labels)

        category_counts = df['Catégorie'].value_counts()
        category_counts = category_counts.reindex(labels, fill_value=0)

        colors = mcolors.LinearSegmentedColormap.from_list("green_to_red", ["green", "yellow", "red"])(np.linspace(0, 1, len(labels)))
        label_color_dict = {label: color for label, color in zip(labels, colors)}
        colors_for_plot = [label_color_dict[label] for label in category_counts.index]
        fig, ax = plt.subplots()
        #ax.pie(category_counts, labels=category_counts.index, autopct='%1.1f%%', colors=colors_for_plot)
        wedges, texts, autotexts = ax.pie(category_counts, colors=colors, shadow=True, autopct='%1.1f%%')
        plt.legend(wedges, labels, title="Categories", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        ax.set_title("Delay pie chart")
        plt.tight_layout()
        
        return fig
    
    @output
    @render.plot
    def table():
        
        df = filtered_data()
        
        stats = {
            " ": ["Max", "Mean", "Median"],
            "Delay [min]": [
                df["Delay"].max(),
                round(df["Delay"].mean(), 2),
                df["Delay"].median()],
            "Relative Duration [%]": [
                df["RelativeDuration"].max(),
                round(df["RelativeDuration"].mean(), 2),
                df["RelativeDuration"].median()],
        }

        stats_df = pd.DataFrame(stats)

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.axis("off")

        table = ax.table(
            cellText=stats_df.values,
            colLabels=stats_df.columns,
            cellLoc="center",
            loc="center",
            colColours=["#f7f7f7"] * len(stats_df.columns),
            cellColours=[["#e9e9e9"] * len(stats_df.columns)] * len(stats_df)
        )

        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1.2, 1.2)

        plt.title("Delay stats", pad=20, fontsize=14, fontweight="bold")

        plt.tight_layout()
        
        return fig



app = App(app_ui, server)