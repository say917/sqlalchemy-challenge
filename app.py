# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import pandas as pd
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# Declare a Base using `automap_base()`
Base = automap_base()
# Use the Base class to reflect the database tables
Base.prepare(engine, reflect=True)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/<start><br/>"
        f"/api/v1.0/temp/<start>/<end>"        
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
     #Calculate the most recent date in data
    most_recent = dt.datetime.strptime('2017-08-23','%Y-%m-%d').date()

    #Calculate the date 1 year ago from most recent date
    year_from = most_recent - dt.timedelta(days=365)

    #Query for prcp observations for a specific station
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_from).all()
    
    #Convert the query results to a dictionary
    #precip = {date.strptime('%Y-%m-%d'): prcp for date, prcp in precipitation}
    precip = list(np.ravel(precipitation))
    #Return JSON
    return jsonify(precip=precip)

@app.route("/api/v1.0/stations")
def stations():
    outcome = session.query(Station.station).all()
    stations = list(np.ravel(outcome))
    return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def temperature():
    #Calculate the most recent date in data
    most_recent = dt.datetime.strptime('2017-08-23','%Y-%m-%d').date()

    #Calculate the date 1 year ago from most recent date
    year_from = most_recent - dt.timedelta(days=365)
    
    #Query for temperature observations for a specific station
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= year_from).all()
    
    #Convert query results to a list of temperatures
    temps = list(np.ravel(results))

    #Return JSON
    return jsonify(temps=temps)

@app.route("/api/v1.0/temp/<start>")
def start_date(start):

    #Create query for min, avg and max
    start_date_tobs_results = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    
    #Create a list
    start_date_tobs_values =[]
    #Run a for loop for min, avg and max
    for min, avg, max in start_date_tobs_results:
        start_date_tobs_dict = {}
        start_date_tobs_dict["min"] = min
        start_date_tobs_dict["average"] = avg
        start_date_tobs_dict["max"] = max
        start_date_tobs_values.append(start_date_tobs_dict)
    
    #Return JSON
    return jsonify(start_date_tobs_values)

  
@app.route("/api/v1.0/temp/<start>/<end>")
def temp(start,end=None):
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    temps = []
    for min_temp, avg_temp, max_temp in results:
        temps_dict = {}
        temps_dict['Minimum Temperature'] = min_temp
        temps_dict['Average Temperature'] = avg_temp
        temps_dict['Maximum Temperature'] = max_temp
        temps.append(temps_dict)

    return jsonify(temps)

    if __name__ == "__main__":
        app.run(debug=True)


