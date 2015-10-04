from app import app
from flask import render_template, request, jsonify
import pymysql as mdb

import yelp_dataset.neighborhoods as neighborhoods
from yelp_dataset.neighborhoods import CityNeighborhood, unpickle
import cPickle as pickle
import numpy as np
import pandas as pd
import os
import json


dirname = os.path.join(os.path.dirname(__file__),"../")

bos = unpickle(dirname+'bos.pickle')
nyc = unpickle(dirname+'nyc.pickle')



def bounds_poly(polygon):
    lats = [vertex['lat'] for vertex in polygon]
    lons = [vertex['lng'] for vertex in polygon]
    lat_span= max(lats) - min(lats)
    lon_span= max(lons) - min(lons)
    north = max(lats)
    east = max(lons)
    west = min(lons)
    south = min(lats)
    return south,west,north,east

@app.route('/Boston')
@app.route('/')
def cities_input_bos():
  return render_template("input.html",nosuccess = "",home_city= 'Boston',away_city="NYC")

@app.route('/NYC')
def cities_input_nyc():
  return render_template("input2.html",nosuccess = "",home_city= "NYC",away_city="Boston")

def write_keywords_weights(keywords,weights):
    return [{"letter": k,"frequency": w} for k,w in zip(keywords,weights)]


@app.route('/output')
def cities_output():

    address = request.args.get('address')
    city = request.args.get('city')
    if city =="Boston":
        hcity = bos
        acity = nyc
        away_city = "NYC"
    elif city== 'NYC':
        hcity = nyc
        acity = bos
        away_city = "Boston"
    input_nid = hcity.index_lookup(address)

    if input_nid == None:
        return render_template("input.html",nosuccess = "Please Enter Valid Neighborhood",home_city=city,away_city=away_city)

    home_name = hcity.neighborhoods[input_nid]
    home_neighborhood = hcity.getVector(input_nid)
    input_polygon = hcity.neighborhood_polygon(input_nid)
    input_bounds = bounds_poly(input_polygon)

    output_nid = acity.find_similar_to_ref(home_neighborhood,num_results=1)[0]
    away_name= acity.neighborhoods[output_nid]
    output_polygon = acity.neighborhood_polygon(output_nid)
    output_bounds = bounds_poly(output_polygon)

    #keywords = nyc.getKeyWords(home_neighborhood,num_results=10)
    keywords,weights = neighborhoods.getKeywords(hcity,acity,input_nid,output_nid)
    kw= write_keywords_weights(keywords,weights)

    return render_template("output.html",
            home_city = city,
            home_name= home_name,
            away_name = away_name,
            input_polygon=input_polygon,output_polygon= output_polygon,
            input_bounds=input_bounds, output_bounds= output_bounds,
            keywords=keywords,kw=kw)


@app.route('/autocomplete',methods=['GET'])
def autocomplete():
    keyword = request.args.get('keyword')
    city = request.args.get('city')
    if city == 'Boston':
        hcity = bos
    if city == 'NYC':
        hcity = nyc
    if keyword:
        results = {(i+1):v for i,v in enumerate(hcity.neighborhoods) \
                if v.lower().startswith(keyword.lower()) }
    else:
        results = {(i+1):v for i,v in enumerate(hcity.neighborhoods)}
    return jsonify(data=results)
