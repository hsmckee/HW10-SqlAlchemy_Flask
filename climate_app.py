### Step 2 - Climate App
from flask import Flask, request, jsonify, escape
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import func 
import datetime 

#Now that you have completed your initial analysis, design a Flask API based 
#on the queries that you have just developed.

#* Use FLASK to create your routes.
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:/Users/hollymckee/Desktop/ \
UT-MCB-DATA-PT-11-2019-U-C/ \
Homework/10-Advanced-Data-Storage-and-Retrieval/Instructions/Resources/hawaii.sqlite'
db = SQLAlchemy(app)

#### Routes

class DictMixIn: 
    def to_dict(self):
        return {
            column.name: getattr(self, column.name)
            if not isinstance(getattr(self, column.name), datetime.datetime)
            else getattr(self, column.name).isoformat()
            for column in self.__table__.columns
        }

class Measurement(db.Model, DictMixIn):
    __tablename__ = "measurement"
    id = db.Column(db.Integer(), primary_key=True)
    station = db.Column(db.String())
    date = db.Column(db.Date())
    prcp = db.Column(db.Float())
    tobs = db.Column(db.Float())


class Station(db.Model, DictMixIn):
    __tablename__ = "station"
    id = db.Column(db.Integer(), primary_key=True)
    station = db.Column(db.String())
    name = db.Column(db.String())
    latitude = db.Column(db.Float())
    longitude = db.Column(db.Float())
    elevation = db.Column(db.Float())



#  * List all routes that are available.
@app.before_first_request
def init_app():
    db.create_all()

@app.route("/")
def home():
    return (
        f"<h1>Available routes.</h1> <br/>"
        f"<ul>"
        f"<li>/api/v1.0/precipitation</li>"
        f"<li>/api/v1.0/stations </li>"
        f"<li>/api/v1.0/tobs </li>"
        f"<li>/api/v1.0/&lt;start&gt; </li>"
        f"<li>/api/v1.0/&lt;start&gt;/&lt;end&gt; </li>"
        f"</ul>"
        )

@app.route('/api/v1.0/precipitation')
def prcp_page():
    data = (db.session.query(Measurement, func.sum(Measurement.prcp).label('total_prcp'))
                            .filter(Measurement.date > '2016-08-23')
                            .group_by(Measurement.date)
                            .all())
    clean_data = [[row[0].to_dict(), row[1]] for row in data] 
    result = {}
    for row in clean_data:
        result[f"Date: {row[0]['date']}"] = f"Total Prcp: {row[1]}"
    return jsonify(result)

@app.route('/api/v1.0/stations')
def station_page():
    data = Station.query.all()
    return jsonify([row.to_dict() for row in data])

@app.route('/api/v1.0/tobs')
def tobs_page():

    data = (db.session.query(Measurement, func.count(Measurement.tobs).label('Temperature Obs'))
                            .filter(Measurement.date > '2016-08-23')
                            .group_by(Measurement.date)
                            .all())
    clean_data = [[row[0].to_dict(), row[1]] for row in data]                             
    result = {}
    for row in clean_data:
        result[f"Date: {row[0]['date']}"] = f"Temp Observations: {row[1]}"
    return jsonify(result)

@app.route('/api/v1.0/<start>')
def tobs_query_start(start):
    try:
        data = (db.session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))
                                .filter(Measurement.date >= f"{start}")
                                .all())
        result = [f"Start Date : {start}",
                f"End Date :   2017-08-23",
                f"Minimum Temp : {data[0][0]}",
                f"Average Temp : {data[0][1]}",
                f"Maximum Temp : {data[0][2]}"  
        ]
        return jsonify(result)

    except Exception as e:
        return jsonify({"status": "failure", "error": str(e)})

@app.route('/api/v1.0/<start>/<end>')
def tobs_query_end(start, end):
    try:
        data = (db.session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))
                                .filter(Measurement.date >= f"{start}")
                                .filter(Measurement.date <= f"{end}")
                                .all())

        result = [f"Start Date : {start}",
                f"End Date :   {end}",
                f"Minimum Temp : {data[0][0]}",
                f"Average Temp : {data[0][1]}",
                f"Maximum Temp : {data[0][2]}"  
        ]
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"status": "failure", "error": str(e)})    


if __name__ == "__main__":
    app.run(debug=True)

