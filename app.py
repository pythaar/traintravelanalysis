import os
import json
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta, date

STATION_NAME = ["Lille", "Lorient", "Paris Gare du Nord", "Paris Montparnasse", "Rennes", "Aulnoye-Aymeries", "Valenciennes", "Amiens", "Abbeville", "Saint-Quentin"]

def createDBIfNot(path_list):
    
    header = "Origin,Destination,Year,Month,Day,PlannedDeparture,RealDeparture,PlannedArrival,RealArrival,Comment"
    
    for path in path_list:
        if not os.path.exists(path):
            with open(path, 'w') as database:
                database.write(header + '\n')
                database.close()

def checkStationInput(origin, destination):
    
    if origin == destination:
        st.error('Origin and destination station are identical')
        if st.button('Refresh'):
            st.rerun()
    else:
        return True

def addToDatabase(db_path, origin, destination, train_date, departure, real_departure, arrival):

    datas = origin + ',' + destination + ',' + str(train_date.year) + ',' + str(train_date.month) + ',' + str(train_date.day)
    datas = datas + ',' + departure.strftime("%H:%M") + ',' + real_departure.strftime("%H:%M")
    datas = datas + ',' + arrival.strftime("%H:%M") + ',' + arrival.strftime("%H:%M")
    datas = datas + ',,' + 'False'
    
    with open(db_path, 'a') as database:
            database.write(datas + '\n')
            database.close()
    

def addTravel(db_path):
    
    st.subheader("Add a travel")
    origin = st.selectbox('Origin', STATION_NAME)
    destination = st.selectbox('Destination', STATION_NAME)
    train_date = st.date_input('Date')
    planned_departure = st.time_input('Planned Departure')
    real_departure = st.time_input('Real Departure')
    planned_arrival = st.time_input('Planned Arrival')
    if st.button('Add train'):
        station_ok = checkStationInput(origin, destination)
        if station_ok:
            addToDatabase(db_path, origin, destination, train_date, planned_departure, real_departure, planned_arrival)
            st.rerun()
    
def displayNotCorrectedTrains(db_path, temp_db_path):
    
    train_df = pd.read_csv(temp_db_path)
    train_df["Corrected"] = False
    columns_name = train_df.columns
    updated_train_df = st.data_editor(
                            train_df,
                            column_config={"Corrected": st.column_config.CheckboxColumn("Corrected",help="Check if train datas are ok",default=False),
                                           "RealArrival": st.column_config.TextColumn("RealArrival",help="Real arrival"),
                                           "Comment": st.column_config.TextColumn("Comment",help="Comment about delay")
                            },
                            disabled=['Origin','Destination','Year','Month','Day','PlannedDeparture','RealDeparture','PlannedArrival'],
                            hide_index=True,
                        )
    
    if st.button('Add to database'):
    
        corrected = train_df[train_df['Corrected'] == True].drop(columns=['Corrected'])
        non_correced = train_df[train_df['Corrected'] == False].drop(columns=['Corrected'])
        
        non_correced.to_csv(temp_db_path)
        
        df_database = pd.read_csv(db_path)
        df_database = pd.concat([df_database, corrected], ignore_index=True)
        df_database.to_csv(db_path)
        st.rerun()
    
    
def main():
    
    st.title('Train travel analysis')
    st.subheader('By Jules aka Pytpyt')
    st.divider()

    #Make sure traindatabase exists
    db_path = 'trainDataBase.csv'
    temp_db_path = 'tempDataBase.csv'
    createDBIfNot([db_path, temp_db_path])
    
    tab1, tab2, tab3 = st.tabs(["Add a train", "Add train delay", "Stats"])
    
    with tab1:
        addTravel(temp_db_path)
        
    with tab2:
        displayNotCorrectedTrains(db_path, temp_db_path)

if __name__ == "__main__":
    main()