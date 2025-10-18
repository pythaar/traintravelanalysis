import os
import sys
import json
import pandas as pd
GIT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(GIT_PATH)
from datetime import datetime, timedelta

def convert_times(year, month, day, dep_time, prevarr_time, realarr_time):
    # Conversion des heures en datetime
    dep_datetime = datetime.strptime(dep_time, "%H:%M").replace(
        year=year, month=month, day=day
    )
    prevarr_datetime = datetime.strptime(prevarr_time, "%H:%M").replace(
        year=year, month=month, day=day
    )
    
    realarr_datetime = datetime.strptime(realarr_time, "%H:%M").replace(
        year=year, month=month, day=day
    )

    # Si l'heure d'arrivée est antérieure à celle de départ, on ajoute un jour
    if prevarr_datetime < dep_datetime:
        prevarr_datetime += timedelta(days=1)
    
    if realarr_datetime < dep_datetime:
        realarr_datetime += timedelta(days=1)

    return dep_datetime, prevarr_datetime, realarr_datetime


with open(os.path.join(GIT_PATH, 'savedb.json'), 'r') as json_input:
    json_db = json.load(json_input)
df = pd.DataFrame(json_db["trainList"])

with open(os.path.join(GIT_PATH, 'database', 'stations_info.json'), 'r') as json_input:
    stations_info = json.load(json_input)
with open(os.path.join(GIT_PATH, 'database', 'stations_distance.json'), 'r') as json_input:
    stations_distance = json.load(json_input)


    
for i_row, row in df.iterrows():
    
    origin = row['Origin']
    destination = row['Destination']
    if origin not in stations_distance:
        print(f'{origin} not known')
    else:
        if destination not in stations_distance[origin]:
            print(f'{destination} not in {origin}')
        else:
            if row['Type'] not in stations_info[origin]['Compagny']:
                print(f'Compagny error: {row["Type"]} not in {origin}, at {row["Day"]}-{row["Month"]}-{row["Year"]}')
            if row['Type'] not in stations_info[destination]['Compagny']:
                print(f'Compagny error: {row["Type"]} not in {destination}, at {row["Day"]}-{row["Month"]}-{row["Year"]}')
            departure, prevarr, realarr = convert_times(row['Year'], row['Month'], row['Day'], row['Departure'], row['Arrival'], row['RealArrival'])
            delay_datetime = realarr - prevarr
            delay = int(delay_datetime.total_seconds() / 60)
            if delay != row['Delay']:
                print('ERROR DELAY', row)
            traveltime_datetime = realarr - departure
            traveltime = int(traveltime_datetime.total_seconds() / 60)
            if traveltime != row['TravelTime']:
                print('ERROR TRAVEL TIME', row)
            speed = round(stations_distance[origin][destination]/(((realarr - departure).total_seconds() / 60)/60),2)
            if row['Speed']!= speed:
                print(f'Speed error: {row["Speed"]} not egal ({speed}) for {origin} - {destination}')
            