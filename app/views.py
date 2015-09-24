from app import app
from flask import render_template, request
import pymysql as mdb
from flask.ext.googlemaps import GoogleMaps, Map
#import yelp_dataset.create_yelp_df as ydf
#import yelp_dataset.extract_features as ef
import yelp_dataset.neighborhoods as neighborhoods
from yelp_dataset.neighborhoods import CityNeighborhood, unpickle
import cPickle as pickle
import numpy as np
import pandas as pd

GoogleMaps(app)

#df_grid = pd.read_pickle('./yelp_dataset/df_grid.pickle')
#similarity_matrix = np.load('./yelp_dataset/similarity_mat.pickle')

bos = unpickle('bos.pickle')
nyc = unpickle('nyc.pickle')

@app.route('/input')
def cities_input():
  return render_template("input.html")

@app.route('/output')
def cities_output():
    #db = mdb.connect(user='root',host='localhost',db="yelp", \
    #    charset = 'utf8')

    #pull 'ID' from input field and store it
    address = request.args.get('address')
    ref_latitude, ref_longitude = neighborhoods.googleGeocoding(address)
    #print ref_latitude
    #print ref_longitude
    #df_sim = ef.similar_grid_points(ref_latitude,ref_longitude,df_grid,
    #                        similarity_matrix,num_results=1)

    #sim_lat = df_sim.latitude.values[0]
    #sim_lon = df_sim.longitude.values[0]
    

    input = {'lat': ref_latitude, 'lng': ref_longitude}

    polygon = bos.neighborhood_containing_point(latlon= (ref_latitude, ref_longitude))
    # [ {'lat': 25.774, 'lng': -80.190},\
    #             {'lat': 18.466, 'lng': -66.118},\
    #             {'lat': 32.321, 'lng': -64.757},\
    #             {'lat': 25.774, 'lng': -80.190} \
    #             ];

    outputmap = Map(
       identifier = "view-side2",
       lat = sim_lat,
       lng = sim_lon,
       markers=[(sim_lat, sim_lon)],
       style = "height:450px;width:600px;margin:0;"
    )

    return render_template("output.html",input=input,
            polygon=polygon,outputmap=outputmap)
