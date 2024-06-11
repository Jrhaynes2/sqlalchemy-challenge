# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# inspector = inspect(engine)
# print(inspector.get_table_names())

# columns= inspector.get_columns('measurement')
# for c in columns:
#     print(c['name'],c["type"])

# Save references to each table
Measurement = Base.classes.measurement
Stations = Base.classes.station

# Create our session (link) from Python to the DB
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
        f"/api/v1.0/start/<start><br/>"
        f"/api/v1.0/start/end/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # # Query 12 mo precipitation data
    sel = [Measurement.date, Measurement.prcp]
    totals = session.query(*sel).filter(Measurement.date >= query_date).order_by(Measurement.date).all()
    print(totals)
    # # Create a dictionary from the row data and append to a list of all_passengers
    precip_dict = {}
    for date, prcp in totals:
        precip_dict[date] = prcp


    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def stations():
        
    # Query all unique station name data
    station_list = session.query(Stations.name).all()

    session.close()

    # Create a list of all unique station names
    Station_names = list(np.ravel(station_list))

    return jsonify(Station_names)

@app.route("/api/v1.0/tobs")
def tobs():

    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # # Query most active station data
    ave = [Measurement.station, Measurement.date, Measurement.tobs]

    # # Create a list of the most active stations in the previous year
    temp_sta = session.query(*ave).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= query_date).\
        order_by(Measurement.date).all()

    active_temp = list(np.ravel(temp_sta))

    return jsonify(active_temp)


@app.route("/api/v1.0/start/<start_date>")
def get_data_by_date(start_date):

    # Convert start_date to a datetime object if needed
    start_date = dt.datetime.strptime(start_date, '%Y-%m-%d')

    # Query the database to get the minimum temperature from start_date to the end of the dataset
    min_temp = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start_date).scalar()
    max_temp = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start_date).scalar()
    avg_temp = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).scalar()

    if min_temp is not None:
        return jsonify({"Minimum temperature": min_temp, "Maximum temperature": max_temp, "Average temperature": avg_temp})
    else:
        return jsonify({"error": f"No temperature data found after {start_date}"}), 404

@app.route("/api/v1.0/start/end/<sta_date>/<end_date>")
def get_data_by_range(sta_date, end_date):

    # Convert start_date to a datetime object if needed
    sta_date = dt.datetime.strptime(sta_date, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end_date, '%Y-%m-%d')

    # Query the database to get the minimum temperature from start_date to the end of the dataset
    min_temp = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= sta_date).filter(Measurement.date < end_date).scalar()
    max_temp = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= sta_date).filter(Measurement.date < end_date).scalar()
    avg_temp = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= sta_date).filter(Measurement.date < end_date).scalar()

    if min_temp is not None:
        return jsonify({"Minimum temperature": min_temp, "Maximum temperature": max_temp, "Average temperature": avg_temp})
    else:
        return jsonify({"error": f"No temperature data found after {sta_date}"}), 404


if __name__ == '__main__':
    app.run(debug=True)