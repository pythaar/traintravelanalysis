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

def createDatabaseIfNot(file_path):
    
    json_dict = {"expenses": {"Work": 0, "TGVMAX": 0, "Cancel": 0, "Other": 0}, "trainList": []}
    if not os.path.exists(file_path):
        with open(file_path, 'w') as json_file:
            json.dump(json_dict, json_file)
            
def checkTrainStation(train_to_check, station_db):
    
    origin = train_to_check["Origin"]
    destination = train_to_check["Destination"]
    list_stations = [origin, destination]
    list_stations.sort()
    
    if list_stations[1] in list(station_db[list_stations[0]].keys()):
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
    new_train["Day"] = int(date.day)
    new_train["Month"] = int(date.month)
    new_train["Year"] = int(date.year)
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
    train_type = add_train.selectbox("Train type", ("TER HDF", "TGV INOUI", "BREIZHGO", "OUIGO", "Eurostar"))
    price = add_train.number_input('Price')
    if add_train.button('Add train'):
        new_train = toDict(origin, destination, date, departure, arrival, train_type, price)
        train_ok = checkTrainStation(new_train, station_db)
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
        new_train["Destination"] = "Aulnoye-Aymeries"
        new_train["Day"] = int(today.day)
        new_train["Month"] = int(today.month)
        new_train["Year"] = int(today.year)
        new_train["Departure"] = "07:05"
        new_train["Arrival"] = "08:07"
        new_train["Type"] = "TER HDF"
        new_train["Price"] = 0
        
        temp_db.append(new_train)
        with open(temp_db_path, 'w') as json_file:
                json.dump(temp_db, json_file)
        st.rerun()
    if st.button("Add Aulnoye-Lille"):
        
        with open(temp_db_path, 'r') as json_file:
            temp_db = json.load(json_file)
        
        new_train = {}
        new_train["Origin"] = "Aulnoye-Aymeries"
        new_train["Destination"] = "Lille Flandres"
        new_train["Day"] = int(today.day)
        new_train["Month"] = int(today.month)
        new_train["Year"] = int(today.year)
        new_train["Departure"] = "17:52"
        new_train["Arrival"] = "18:55"
        new_train["Type"] = "TER HDF"
        new_train["Price"] = 0
        
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

def computeDelay(ref_time, compared_time, addDay):
    
    ref_min = timeToMin(ref_time)
    compared_min = timeToMin(compared_time)
    if addDay:
        return compared_min - ref_min + 60*24
    else:
        return compared_min - ref_min


def computeTravelTime(departure, arrival):
    
    arr = datetime.strptime(arrival, "%H:%M").time()
    dep = datetime.strptime(departure, "%H:%M").time()
    if arr < dep:
        return timeToMin(arr) - timeToMin(dep) + 60*24
    else:
        return timeToMin(arr) - timeToMin(dep)

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
    
def deleteTrain(temp_db, temp_db_path, train_idx):

    temp_db.pop(train_idx)
    with open(temp_db_path, 'w') as json_file:
        json.dump(temp_db, json_file)
    st.rerun()

def getDistance(origin, destination, db_path):
    
    with open(db_path, 'r') as json_file:
        db = json.load(json_file)
    
    list_stations = [origin, destination]
    list_stations.sort()
    distance = db[list_stations[0]][list_stations[1]]
    
    return distance   
        
def updateTrain(temp_db_path, db_path, station_db_path):
    
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
        real_arrival = mod_train.time_input('Real arrival time', value=planned_arrival)
        comment = mod_train.text_input('Comment')
        addDay = mod_train.checkbox("The planned arrival was the day before the real arrival")
        delay = computeDelay(planned_arrival, real_arrival, addDay)
        output_delay = getTextDelay(delay)
        mod_train.caption(output_delay)
        if mod_train.button("Apply"):
            with open(db_path, 'r') as json_file:
                db = json.load(json_file)
            train["RealArrival"] = real_arrival.strftime("%H:%M")
            train["Delay"] = delay
            train["Comment"] = comment
            distance = getDistance(train["Origin"], train["Destination"], station_db_path)
            train["Distance"] = distance
            TravelTime = computeTravelTime(train["Departure"], train["RealArrival"])
            train["TravelTime"] = TravelTime
            train["Speed"] = round(distance/(TravelTime/60),2)
            train["RelativeDuration"] = round((TravelTime / (TravelTime - delay))*100,2)
            db["trainList"].append(train)
            with open(db_path, 'w') as json_file:
                json.dump(db, json_file)
            temp_db.pop(train_idx)
            with open(temp_db_path, 'w') as json_file:
                json.dump(temp_db, json_file)
            st.rerun()
                
def displayDatabase(db_path):
    with open(db_path, 'r') as json_file:
        db = json.load(json_file)
    
    if db["trainList"]:
        df_db = pd.DataFrame(db["trainList"])
        st.dataframe(df_db)
    else:
        st.error("No train recorded")
        
def getStrTime(totalTime):
    
    days = totalTime // (24 * 60)
    hours = (totalTime % (24 * 60)) // 60
    minutes = totalTime % 60

    return f"{days} Day, {hours} Hours and {minutes} Minutes"

def getStrPercent(value, n_train):
    
    return str(round(100*value/n_train,2)) + "%"

def displayStats(db_path):
    
    with open(db_path, 'r') as json_file:
        db = json.load(json_file)
    
    df_db = pd.DataFrame(db["trainList"])
    expenses = db["expenses"]
    total_expenses = 0
    for key, value in expenses.items():
        total_expenses += value
    
    total_expenses += df_db["Price"].sum()
    
    n_train = df_db.shape[0]
    st.text("Total train taken: " + str(n_train))
    st.text("Total spent: " + str(round(total_expenses, 2)) + " €")
    strTime = getStrTime(df_db["TravelTime"].sum())
    st.text("Total time on train: " + strTime)
    st.text("Distance travelled: " + str(round(df_db["Distance"].sum())) + " km")
    st.text("Average speed: " + str(round(df_db["Speed"].mean(), 2)) + " km/h")
    
    st.divider()
    strDelay = getStrTime(df_db["Delay"].sum())
    st.text("Total delay: " + strDelay)
    st.text("Average delay: " + str(round(df_db["Delay"].mean(), 2)) + " mins")
    st.text("Median delay: " + str(round(df_db["Delay"].median())) + " mins")
    
    early = (df_db['Delay'] < -1).sum()
    on_time = ((df_db['Delay'] >= -1) & (df_db['Delay'] <= 1)).sum()
    low_delay = ((df_db['Delay'] > 1) & (df_db['Delay'] <= 5)).sum()
    delay = ((df_db['Delay'] > 5) & (df_db['Delay'] <= 10)).sum()
    big_delay = ((df_db['Delay'] > 10) & (df_db['Delay'] <= 30)).sum()
    very_big_delay = (df_db['Delay'] > 30).sum()
    
    early_delta = getStrPercent(early, n_train)
    on_time_delta = getStrPercent(on_time, n_train)
    low_delay_delta = getStrPercent(low_delay, n_train)
    delay_delta = getStrPercent(delay, n_train)
    big_delay_delta = getStrPercent(big_delay, n_train)
    very_big_delay_delta = getStrPercent(very_big_delay, n_train)
    
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)
    col1.metric("Early", early, delta=early_delta)
    col2.metric("On time", on_time, delta=on_time_delta)
    col3.metric("Low delay (<5 mins)", low_delay, delta=low_delay_delta, delta_color="off")
    col4.metric("Delay (Between 5 and 10 mins)", delay, delta=delay_delta, delta_color="off")
    col5.metric("Big delay (Between 10 and 30 mins)", big_delay, delta=big_delay_delta, delta_color="inverse")
    col6.metric("Very big delay (>30 mins)", very_big_delay, delta=very_big_delay_delta, delta_color="inverse")

def addExpenses(db_path):
    
    with open(db_path, 'r') as json_file:
        db = json.load(json_file)
    
    expenses = db["expenses"]
    categories = list(expenses.keys())
    selected_cat = st.selectbox('Category', categories)
    expense_to_add = st.number_input('Value')
    if st.button("Add"):
        db["expenses"][selected_cat] += expense_to_add
        with open(db_path, 'w') as json_file:
            json.dump(db, json_file)
        st.rerun()
        
    

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
    createDatabaseIfNot(db_path)
    
    tab1, tab2, tab3 = st.tabs(["Add train", "See database", "Stats"])
    with tab1:
        addNewTrain(temp_db_path, station_db)
        
        st.subheader('Trains to be updated')
        displayTempDB(temp_db_path)
        
        st.subheader('Update a train')
        updateTrain(temp_db_path, db_path, station_db)
        
        st.subheader('Reccurent trains')
        lilleaulnoye(temp_db_path)
        
        st.subheader('Add expense')
        addExpenses(db_path)
    
    with tab2:
        st.subheader("Database")
        displayDatabase(db_path)
    
    with tab3:
        st.subheader("Stats")
        st.divider()
        st.subheader("Global")
        displayStats(db_path)
    
if __name__ == "__main__":
    main()