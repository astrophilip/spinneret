from app import app
from flask import render_template, request
import pymysql as mdb
from flask.ext.googlemaps import GoogleMaps, Map
import yelp_dataset.create_yelp_df as ydf
import yelp_dataset.extract_features as ef
import numpy as np
import pandas as pd

GoogleMaps(app)

df_grid = pd.read_pickle('./yelp_dataset/df_grid.pickle')
similarity_matrix = np.load('./yelp_dataset/similarity_mat.pickle')

@app.route('/input')
def cities_input():
  return render_template("input.html")

@app.route('/output')
def cities_output():
    db = mdb.connect(user='root',host='localhost',db="yelp", \
        charset = 'utf8')

    #pull 'ID' from input field and store it
    address = request.args.get('address')

    ref_latitude, ref_longitude = ef.googleGeocoding(address)
    #print ref_latitude
    #print ref_longitude
    df_sim = ef.similar_grid_points(ref_latitude,ref_longitude,df_grid,
                            similarity_matrix,num_results=1)

    sim_lat = df_sim.latitude.values[0]
    sim_lon = df_sim.longitude.values[0]

    inputmap = Map(
       identifier = "view-side",
       lat = ref_latitude,
       lng = ref_longitude,
       markers=[(ref_latitude, ref_longitude)],
       style = "height:450px;width:600px;margin:0;"
    )

    outputmap = Map(
       identifier = "view-side2",
       lat = sim_lat,
       lng = sim_lon,
       markers=[(sim_lat, sim_lon)],
       style = "height:450px;width:600px;margin:0;"
    )

    #Output the qualities that are important

    # with db:
    #     cur = db.cursor()
    #     #just select the city from the world_innodb that the user inputs
    #     cur.execute("SELECT business_id, category FROM bus_cat WHERE category='%s';" % bus)
    #     query_results = cur.fetchall()
    spots = ['a','b','c']
    # bus = []
    # for result in query_results:
    #     bus.append(dict(business_id=result[0], category=result[1]))
    #     the_result = ''
    the_result = ''
    return render_template("output.html", inputmap=inputmap,outputmap=outputmap)
