from sqlalchemy import create_engine, text
import pandas as pd
from datetime import datetime, timedelta
import os
import sys
import json
GIT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(GIT_PATH)
from config import DB_URL

def add_train(origin, destination, departure, scheduled, arrival, company, comment, delay, distance, traveltime, speed, relduration):
    
    engine = create_engine(DB_URL)
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO trainsdb (origin, destination, departure, scheduled, arrival, company, comment, delay, distance, traveltime, speed, relduration)
            VALUES (:origin, :destination, :departure, :scheduled, :arrival, :company, :comment, :delay, :distance, :traveltime, :speed, :relduration);
        """), {
            "origin": origin, 
            "destination": destination, 
            "departure":departure, 
            "scheduled":scheduled, 
            "arrival":arrival, 
            "company":company, 
            "comment":comment, 
            "delay":delay, 
            "distance":distance, 
            "traveltime":traveltime, 
            "speed":speed, 
            "relduration":relduration
        })