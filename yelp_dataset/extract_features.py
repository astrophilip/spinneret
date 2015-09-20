import numpy as np
import create_yelp_df as ydf
import pandas as pd
from collections import Counter
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity
from geopy.distance import distance
import urllib
import json

REARTH = 3959.0 #miles
STEP = 0.3 #miles
RAD = np.radians(1)

def nonsense():
    pass

def googleGeocoding(address):
    """This function takes an address and returns the latitude and longitude
    from the Google geocoding API."""
    baseURL = 'http://maps.googleapis.com/maps/api/geocode/json?'
    geocodeURL = baseURL + 'address=' + address #+'&key=' + key
    geocode = json.loads(urllib.urlopen(geocodeURL).read())
    lat = geocode['results'][0]['geometry']['location']['lat']
    lon = geocode['results'][0]['geometry']['location']['lng']
    return lat, lon

def find_estab(lat,lon, dist, dfB):
    # dist in miles
    dlat = dist/REARTH/RAD
    dlon = dist/REARTH/RAD/np.cos(RAD*lat)
    ids =  (abs(dfB.latitude -lat) < dlat ) & (abs(dfB.longitude -lon) < dlon )
    return list(dfB.index[ids])

def point(lat,lon):
    x = np.radians(lon)*np.cos(np.radians(lat))
    y = np.radians(lat)
    return (x,y)

def point_to_coord(x,y):
    lat = np.rad2deg(y)
    lon = x/np.radians(1.0)/np.cos(y)
    return (lat,lon)

def cartesian_prod(x,y):
    return np.array([np.tile(x,len(y)),np.repeat(y,len(x))]).T

def setup_grid(spacing):
    #get grid points given a spacing in miles
    dlat = spacing/REARTH/RAD
    dlon = spacing/REARTH/RAD/np.cos(RAD*33.4)
    lat_pho = np.arange(33.0,34.0,dlat)
    lon_pho = np.arange(-112.6,-111.4,dlon)
    z_pho = cartesian_prod(lat_pho,lon_pho)
    return z_pho

def construct_grid_df(dfB):
    z = setup_grid(STEP)
    latitude, longitude = z[:,0], z[:,1]
    df = pd.DataFrame({'latitude': latitude,'longitude': longitude})
    estab_count = []
    estab_list = []
    for lat,lon in zip(latitude,longitude):
        el = find_estab(lat,lon,STEP,dfB)
        estab_count.append(len(el))
        estab_list.append(el)
    df['estab_count']=estab_count
    df['estab_list']= estab_list
    df = df[df.estab_count > 10]
    df.reset_index(drop=True,inplace=True)
    df.index.name = 'grid_id'
    df['latlon'] = zip(df['latitude'],df['longitude'])
    return df

def construct_grid_cat_counter(df_bus,estab_list):
    cat_counter = Counter()
    for i in estab_list:
        cat_counter.update(df_bus.ix[i,'categories'])
    return cat_counter

def construct_grid_cat_counter_list(df_grid,df_bus):
    #takes a list of cat_counters
    counter_list = []
    for estab_list in df_grid.estab_list:
        cat_count = construct_grid_cat_counter(df_bus,estab_list)
        counter_list.append(cat_count)
    return counter_list

def cat_grid_matrix(counter_list):
    dv= DictVectorizer()
    X = dv.fit_transform(counter_list)

    scaler = TfidfTransformer()
    Xscaled = scaler.fit_transform(X)
    return Xscaled


def nearest_grid_point(lat,lon,df_grid):
    grid_points = df_grid.latlon
    distances = np.array([distance((lat,lon),gp) for gp in grid_points])
    id_min = distances.argmin()
    return id_min

def similar_grid_points(ref_lat,ref_lon, df_grid,similarity_matrix,
                        num_results=10):
    # get grid ids in ascending order
    ref_ind = nearest_grid_point(ref_lat,ref_lon,df_grid)
    ind_sort = np.argsort(similarity_matrix[:,ref_ind])[::-1]
    df = df_grid.ix[ind_sort,['latitude','longitude','latlon']]
    sim = similarity_matrix[ind_sort,ref_ind]
    df['similarity'] = sim
    grid_points = df.latlon
    distances = np.array([distance((ref_lat,ref_lon),gp).miles for gp in grid_points])
    df['distances'] = distances
    df = df[df.distances > 2.0 ]
    return df.head(num_results)

def find_similar_to_ref(lat,lon, idx_grid,df_grid):
    pass
