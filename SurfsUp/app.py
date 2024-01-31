# Import the dependencies.
import numpy as np
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
def home():
    return (
        "Welcome to the Climate App API!<br/>"
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/[start_date format:yyyy-mm-dd]<br/>"
        "/api/v1.0/[start_date format:yyyy-mm-dd]/[end_date format:yyyy-mm-dd]<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
# Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using
# date as key and prcp as the value. Return the JSON representation of your dictionary.
    
# Calculate the date one year from the last date in the dataset
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d').date()
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    # Query the last 12 months of precipitation data
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
                        filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a dictionary
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    # Close the session
    session.close()

    return jsonify(precipitation_dict)

# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    # Query all stations from the dataset
    stations_data = session.query(Station.station).all()

    # Convert the query results to a list
    stations_list = [station[0] for station in stations_data]

    # Close the session
    session.close()

    return jsonify(stations_list)

# Query the dates and temperature observations of the most-active station for the previous year of data.
# Return a JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    # Identify the most active station
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
                            group_by(Measurement.station).\
                            order_by(func.count(Measurement.station).desc()).first()

    most_active_station_id = most_active_station[0]

    # Calculate the date one year from the last date in the dataset
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d').date()
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    # Query the dates and temperature observations of the most active station for the previous year
    temperature_data = session.query(Measurement.date, Measurement.tobs).\
                        filter(Measurement.station == most_active_station_id).\
                        filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a list of dictionaries
    temperature_list = [{"Date": date, "Temperature": tobs} for date, tobs in temperature_data]

    # Close the session
    session.close()

    return jsonify(temperature_list)

#/api/v1.0/<start> and /api/v1.0/<start>/<end>
# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.

@app.route("/api/v1.0/<start>")
def temperature_stats_start(start):
    session = Session(engine)
    try:
        # Query temperature statistics for a specified start date
        temperature_stats = session.query(func.min(Measurement.tobs),
                                          func.avg(Measurement.tobs),
                                          func.max(Measurement.tobs)).\
                            filter(Measurement.date >= start).all()

        # Convert the query results to a list of dictionaries
        temperature_stats_list = [{"TMIN": tmin, "TAVG": tavg, "TMAX": tmax} for tmin, tavg, tmax in temperature_stats]

        return jsonify(temperature_stats_list)
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        # Close the session
        session.close()

@app.route("/api/v1.0/<start>/<end>")
def temperature_stats_start_end(start, end):
    session = Session(engine)
    try:
        # Query temperature statistics for a specified start and end date
        temperature_stats = session.query(func.min(Measurement.tobs),
                                          func.avg(Measurement.tobs),
                                          func.max(Measurement.tobs)).\
                            filter(Measurement.date >= start).\
                            filter(Measurement.date <= end).all()

        # Convert the query results to a list of dictionaries
        temperature_stats_list = [{"TMIN": tmin, "TAVG": tavg, "TMAX": tmax} for tmin, tavg, tmax in temperature_stats]

        return jsonify(temperature_stats_list)
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        # Close the session
        session.close()


if __name__ == "__main__":
    app.run(debug=True)