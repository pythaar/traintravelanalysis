import os
import json
import requests
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta, date

def createJsonIfNot(file_path):
    
    json_dict = []
    if not os.path.exists(file_path):
        with open(file_path, 'w') as json_file:
            json.dump(json_dict, json_file)
            
def checkTrainStation(train_to_check, station_db):
    
    origin = train_to_check["Origin"]
    destination = train_to_check["Destination"]
    if destination in station_db[origin] and origin in station_db[destination]:
        return True
    else:
        error_db_path = 'trainError.json'
        createJsonIfNot(error_db_path)
        with open(error_db_path, 'r') as json_file:
            error_db = json.load(json_file)
        error_db.append(train_to_check)
        with open(error_db_path, 'w') as json_file:
            json.dump(error_db, json_file)
        st.error(origin + ' to ' + destination + ' does not exist in database. It has been added to the error database')
        if st.button('OK'):
            st.rerun()

def toDict(origin, destination, date, departure, arrival, train_type, price):
    
    new_train = {}
    new_train["Origin"] = origin
    new_train["Destination"] = destination
    new_train["Day"] = str(date.day)
    new_train["Month"] = str(date.month)
    new_train["Year"] = str(date.year)
    new_train["Departure"] = departure.strftime("%H:%M")
    new_train["Arrival"] = arrival.strftime("%H:%M")
    new_train["Type"] = train_type
    new_train["Price"] = price
    
    return new_train

def addNewTrain(temp_db_path, station_db):
    
    with open(temp_db_path, 'r') as json_file:
        temp_db = json.load(json_file)
        
    with open(station_db, 'r') as json_file:
        station_db = json.load(json_file)
        
    add_train = st.expander('Add a train to database')
    new_train = {}
    origin = add_train.selectbox('Origin', station_db["stations"])
    destination = add_train.selectbox('Destination', station_db["stations"])
    date = add_train.date_input('Date', format='DD/MM/YYYY')
    departure = add_train.time_input('Departure Time')
    arrival = add_train.time_input('Arrival Time (Planned)')
    train_type = add_train.selectbox("Train type", ("TER HDF", "TGV INOUI", "BREIZHGO", "OUIGO"))
    price = add_train.number_input('Price')
    if add_train.button('Add train'):
        new_train = toDict(origin, destination, date, departure, arrival, train_type, price)
        train_ok = checkTrainStation(new_train, station_db)
        if train_ok:
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

def timeToMin(time):
    
    return time.hour*60+time.minute

def computeDelay(ref_time, compared_time):
    
    ref_min = timeToMin(ref_time)
    compared_min = timeToMin(compared_time)
    return compared_min - ref_min

def getTextDelay(delay):
    
    hours = delay // 60
    mins = delay - hours*60
    if hours != 0:
        return "Train delay: " + str(hours) + "h{:02}".format(mins)
    else:
        return "Train delay: " + str(mins) + " mins"
        
def updateTrain(temp_db_path, db_path):
    
    with open(temp_db_path, 'r') as json_file:
        temp_db = json.load(json_file)
        
    if temp_db:
        n_trains = len(temp_db)
        train_idx = st.number_input("Index of train to modify", min_value=0, max_value=n_trains-1)
        mod_train = st.expander('Modify the train')
        train = temp_db[train_idx]
        mod_train.json(train)
        planned_arrival = datetime.strptime(train["Arrival"], "%H:%M").time()
        real_arrival = mod_train.time_input('Real arrival time', value=planned_arrival)
        comment = mod_train.text_input('Comment')
        delay = computeDelay(planned_arrival, real_arrival)
        output_delay = getTextDelay(delay)
        mod_train.caption(output_delay)
        if mod_train.button("Apply"):
            with open(db_path, 'r') as json_file:
                db = json.load(json_file)
            train["RealArrival"] = real_arrival.strftime("%H:%M")
            train["Delay"] = delay
            train["Comment"] = comment
            db.append(train)
            with open(db_path, 'w') as json_file:
                json.dump(db, json_file)
            temp_db.pop(train_idx)
            with open(temp_db_path, 'w') as json_file:
                json.dump(temp_db, json_file)
            st.rerun()
                
def displayDatabase(db_path):
    with open(db_path, 'r') as json_file:
        db = json.load(json_file)
    
    if db:
        df_db = pd.DataFrame(db)
        st.dataframe(df_db)
    else:
        st.error("No train recorded")
        

def main():
    st.title('Add train to database')
    st.subheader('By Jules aka Pytpyt')
    st.divider()

    st.subheader('New train')
    
    #Make sure json exists
    workdir = os.path.dirname(os.path.abspath(__file__))
    temp_db_path = os.path.join(workdir,'tempDatabase.json')
    db_path = os.path.join(workdir, 'database.json')
    station_db = os.path.join(workdir, "stationDatabase.json")
    createJsonIfNot(temp_db_path)
    createJsonIfNot(db_path)
    
    tab1, tab2 = st.tabs(["Add train", "See database"])
    with tab1:
        addNewTrain(temp_db_path, station_db)
        
        st.subheader('Trains to be updated')
        displayTempDB(temp_db_path)
        
        st.subheader('Update a train')
        updateTrain(temp_db_path, db_path)
    
    with tab2:
        st.subheader("Database")
        displayDatabase(db_path)
    
    
if __name__ == "__main__":
    main()