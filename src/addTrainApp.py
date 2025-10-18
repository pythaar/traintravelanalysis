import os
import sys
import json
import requests
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta, date
GIT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(GIT_PATH)
from config import USER_PSSWD
from src.db_management import add_train as add_train_to_db

def createJsonIfNot(file_path):
    
    json_dict = []
    if not os.path.exists(file_path):
        with open(file_path, 'w') as json_file:
            json.dump(json_dict, json_file)

def checkEmpty(origin, destination, train_company):
    
    train_ok = True
    if origin == " ":
        st.error("The origin is empty")
        train_ok = False
    if destination == " ":
        st.error("The destination is empty")
        train_ok = False
    if train_company == " ":
        st.error("The company is empty")
        train_ok = False
    return train_ok

def toDict(origin, destination, date, departure, arrival, company):
    
    new_train = {}
    new_train["Origin"] = origin
    new_train["Destination"] = destination
    new_train["Day"] = int(date.day)
    new_train["Month"] = int(date.month)
    new_train["Year"] = int(date.year)
    new_train["Departure"] = departure.strftime("%H:%M")
    new_train["Arrival"] = arrival.strftime("%H:%M")
    new_train["Company"] = company
    
    return new_train

def addNewTrain(temp_db_path, stations_info, stations_distance):
    
    with open(temp_db_path, 'r') as json_file:
        temp_db = json.load(json_file)
        
    add_train = st.expander('Add a train to database')
    new_train = {}
    origin_list = [" "] + sorted(list(stations_distance.keys()))
    origin = add_train.selectbox('Origin', origin_list)
    if origin == " ":
        destination = add_train.selectbox('Destination', [" "])
    else:
        destination_list = [" "] + sorted(list(stations_distance[origin].keys()))
        destination = add_train.selectbox('Destination', destination_list)
    date = add_train.date_input('Date', format='DD/MM/YYYY')
    departure = add_train.time_input('Departure Time')
    arrival = add_train.time_input('Scheduled Arrival')
    if destination == " ":
        train_company = add_train.selectbox("Train company", [" "])
    else:
        origin_compagnies = stations_info[origin]["Compagny"]
        destination_compagnies = stations_info[destination]["Compagny"]
        compagnies_list = [" "] + sorted(list(set(origin_compagnies) & set(destination_compagnies)))
        train_company = add_train.selectbox("Train company", compagnies_list)
    if add_train.button('Add train'):
        train_ok = checkEmpty(origin, destination, train_company)
        new_train = toDict(origin, destination, date, departure, arrival, train_company)
        if train_ok:
            temp_db.append(new_train)
            with open(temp_db_path, 'w') as json_file:
                json.dump(temp_db, json_file)
            st.rerun()

def lilleaulnoye(temp_db_path):
    
    today = date.today()
    if st.button("Add Lille-Aulnoye"):
        
        with open(temp_db_path, 'r') as json_file:
            temp_db = json.load(json_file)
        
        new_train = {}
        new_train["Origin"] = "Lille Flandres"
        new_train["Destination"] = "Aulnoye Aymeries"
        new_train["Day"] = int(today.day)
        new_train["Month"] = int(today.month)
        new_train["Year"] = int(today.year)
        new_train["Departure"] = "07:05"
        new_train["Arrival"] = "08:07"
        new_train["Company"] = "TER HDF"
        
        temp_db.append(new_train)
        with open(temp_db_path, 'w') as json_file:
                json.dump(temp_db, json_file)
        st.rerun()
    if st.button("Add Aulnoye-Lille"):
        
        with open(temp_db_path, 'r') as json_file:
            temp_db = json.load(json_file)
        
        new_train = {}
        new_train["Origin"] = "Aulnoye Aymeries"
        new_train["Destination"] = "Lille Flandres"
        new_train["Day"] = int(today.day)
        new_train["Month"] = int(today.month)
        new_train["Year"] = int(today.year)
        new_train["Departure"] = "17:52"
        new_train["Arrival"] = "18:55"
        new_train["Company"] = "TER HDF"
        
        temp_db.append(new_train)
        with open(temp_db_path, 'w') as json_file:
                json.dump(temp_db, json_file)
        st.rerun()
        

def displayTempDB(temp_db_path):
    
    with open(temp_db_path, 'r') as json_file:
        temp_db = json.load(json_file)
    
    if not temp_db:
        st.write('No train to modify')
    else:
        train_df = pd.DataFrame(temp_db)
        st.dataframe(train_df)

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

def deleteTrain(temp_db, temp_db_path, train_idx):

    temp_db.pop(train_idx)
    with open(temp_db_path, 'w') as json_file:
        json.dump(temp_db, json_file)
    st.rerun()

def getTextDelay(delay):
    
    if delay >= 0:
        hours = delay // 60
        mins = delay - hours*60
        if hours != 0:
            return "Train delay: " + str(hours) + "h{:02}".format(mins)
        else:
            return "Train delay: " + str(mins) + " mins"
    else:
        delay = abs(delay)
        hours = delay // 60
        mins = delay - hours*60
        if hours != 0:
            return "Train advance: " + str(hours) + "h{:02}".format(mins)
        else:
            return "Train advance: " + str(mins) + " mins"

def checkPasswd(userpasswd):
    
    if userpasswd == USER_PSSWD:
        return False
    else:
        return True

def updateTrain(temp_db_path, stations_distance):
    
    with open(temp_db_path, 'r') as json_file:
        temp_db = json.load(json_file)
        
    if temp_db:
        n_trains = len(temp_db)
        train_idx = st.number_input("Index of train to modify", min_value=0, max_value=n_trains-1)
        if st.button("Delete this train"):
            deleteTrain(temp_db, temp_db_path, train_idx)
        mod_train = st.expander('Modify the train')
        train = temp_db[train_idx]
        mod_train.json(train)
        planned_arrival = datetime.strptime(train["Arrival"], "%H:%M").time()
        real_arrival = mod_train.time_input('Real arrival time', value=planned_arrival, step=60)
        comment = mod_train.text_input('Comment')
        real_arrival_str = real_arrival.strftime("%H:%M")
        departure, prevarr, realarr = convert_times(train["Year"], train["Month"], train["Day"], train['Departure'], train['Arrival'], real_arrival_str)
        delay_datetime = realarr - prevarr
        delay = int(delay_datetime.total_seconds() / 60)
        output_delay = getTextDelay(delay)
        mod_train.caption(output_delay)
        userpasswd = mod_train.text_input('Password', type='password')
        
        apply_btn_state = checkPasswd(userpasswd)
        if mod_train.button("Apply", disabled=apply_btn_state):
            distance = stations_distance[train['Origin']][train['Destination']]
            traveltime_datetime = realarr - departure
            traveltime = int(traveltime_datetime.total_seconds() / 60)
            duration_scheduled = (prevarr - departure).total_seconds() / 60
            duration_actual = (realarr - departure).total_seconds() / 60
            rela = round((duration_actual / duration_scheduled) * 100, 2)
            speed =  round(distance/(duration_actual/60),2)
            add_train_to_db(train['Origin'], train['Destination'], departure, prevarr, realarr,
                            train['Company'], comment, delay, distance, traveltime, speed, rela)
            temp_db.pop(train_idx)
            with open(temp_db_path, 'w') as json_file:
                json.dump(temp_db, json_file)
            st.rerun()

def main():
    st.title('Add train to database')
    st.subheader('By Jules aka Pytpyt')
    st.divider()

    st.subheader('New train')
    
    #Make sure json exists
    workdir = os.path.dirname(os.path.abspath(__file__))
    temp_db_path = os.path.join(GIT_PATH, 'database','tempDatabase.json')
    createJsonIfNot(temp_db_path)
    with open(os.path.join(GIT_PATH, 'database', 'stations_info.json'), 'r') as json_input:
        stations_info = json.load(json_input)
    with open(os.path.join(GIT_PATH, 'database', 'stations_distance.json'), 'r') as json_input:
        stations_distance = json.load(json_input)
    
    addNewTrain(temp_db_path, stations_info, stations_distance)
    
    st.subheader('Trains to be updated')
    displayTempDB(temp_db_path)
    
    st.subheader('Update a train')
    updateTrain(temp_db_path, stations_distance)
    
    st.subheader('Reccurent trains')
    lilleaulnoye(temp_db_path)
    
    
if __name__ == "__main__":
    main()