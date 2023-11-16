# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite").connect()

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(bind=engine)

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
        f"/api/v1.0/&ltstart&gt<br/>"
        f"/api/v1.0/&ltstart&gt/&ltend&gt"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """ Convert the query results from your precipitation analysis (i.e. 
retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
Return the JSON representation of your dictionary."""
    results = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    dates= dt.date(int(str(results)[2:6])-1, int(str(results)[7:9]) ,int(str(results)[10:12]))
    prcp = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= dates).order_by(Measurement.date.desc()).all()
    #create dictionary
    data = []
    for data1, data2 in session.query(Measurement.date, Measurement.prcp).all():
        data_dict = {}
        data_dict["date"] = data1
        data_dict["precipitation"] = data2
        data.append(data_dict)

    session.close()
    return jsonify(data)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the datasets"""
    results = session.query(Measurement.station,func.count(Measurement.station)).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

    session.close()
    #create dictionary
    data = []
    for data1, data2 in results:
        data_dict = {}
        data_dict["station"] = data1
        data_dict["count"] = data2
        data.append(data_dict)

    return jsonify(data)


@app.route("/api/v1.0/tobs")
def names():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Query the dates and temperature observations of the most-active station for the previous year of data.
    Return a JSON list of temperature observations for the previous year."""
    results = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    dates= dt.date(int(str(results)[2:6])-1, int(str(results)[7:9]) ,int(str(results)[10:12]))
    top_station=list(session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first())[0]
    results = session.query(Measurement.date,Measurement.tobs).\
        filter(Measurement.date >= dates).filter(Measurement.station==top_station).\
        order_by(Measurement.date.desc()).all()

    session.close()
    #create dictionary
    data = []
    for data1, data2 in results:
        data_dict = {}
        data_dict["date"] = data1
        data_dict["Temperature"] = data2
        data.append(data_dict)

    return jsonify(data)

@app.route("/api/v1.0/<start>")
def temp_start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start range.
For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date."""
    lowest=list(session.query(func.min(Measurement.tobs)).\
        filter(Measurement.date>=start).first())[0]
    highest=list(session.query(func.max(Measurement.tobs)).\
        filter(Measurement.date>=start).first())[0]
    average=list(session.query(func.avg(Measurement.tobs)).\
        filter(Measurement.date>=start).first())[0]

    session.close()
    #create dictionary
    data={"Tmin":lowest,
          "Tavg":average,
          "Tmax":highest}
    return jsonify(data)

@app.route("/api/v1.0/<start>/<end>")
def temp_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start-end range.
For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive."""
    lowest=list(session.query(func.min(Measurement.tobs)).\
        filter(Measurement.date>=start).filter(Measurement.date<=end).first())[0]
    highest=list(session.query(func.max(Measurement.tobs)).\
        filter(Measurement.date>=start).filter(Measurement.date<=end).first())[0]
    average=list(session.query(func.avg(Measurement.tobs)).\
        filter(Measurement.date>=start).filter(Measurement.date<=end).first())[0]

    session.close()
    #create dictionary
    data={"Tmin":lowest,
          "Tavg":average,
          "Tmax":highest}
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)