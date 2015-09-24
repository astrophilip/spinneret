import numpy as np
import pandas as pd
from collections import Counter
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial import ConvexHull
import ipdb
import getneighborhoods as gn
import create_new_yelp_df as ydf
from numpy.linalg import norm
from geopy import distance
from shapely.geometry import MultiPoint
import cPickle
import json, urllib

NEIGHBORHOODS = gn.neighborhoods
COUNTS = gn.counts

REARTH = 3959.0 #miles
STEP = 0.3 #miles
RAD = np.radians(1)


def googleGeocoding(address):
    """This function takes an address and returns the latitude and longitude
    from the Google geocoding API."""
    baseURL = 'http://maps.googleapis.com/maps/api/geocode/json?'
    geocodeURL = baseURL + 'address=' + address #+'&key=' + key
    geocode = json.loads(urllib.urlopen(geocodeURL).read())
    lat = geocode['results'][0]['geometry']['location']['lat']
    lon = geocode['results'][0]['geometry']['location']['lng']
    return lat, lon


class CityNeighborhood(object):
    '''
    Collection of Neighborhoods with methods to populate neighborhood
    feautures.
    Provides methods to compare similarities of neighborhoods
    '''
    all_neighborhoods = NEIGHBORHOODS
    all_counts = COUNTS
    def __init__(self,city='BOS',business_df=None, features = None):
        if business_df is None:
            business_df = ydf.create_bus_df_from_neighborhoods(city)

        self.city = city
        self.features = features
        #ipdb.set_trace()

        self.neighborhoods = self.all_neighborhoods[city]
        self.nids = range(len(self.neighborhoods))
        self.business_df = business_df[business_df.city == city]
        self.neighborhood_df = self._construct_neighborhood_df()
        self.X = self._construct_feature_matrix()

    def find_estab(self,lat,lon, dist):
        # dist in miles
        dlat = dist/REARTH/RAD
        dlon = dist/REARTH/RAD/np.cos(RAD*lat)
        ids =  (abs(self.business_df.latitude -lat) < dlat ) & \
                (abs(self.business_df.longitude -lon) < dlon )
        return list(self.business_df.index[ids])


    def _get_cat_counters(self,X):
        cat_list = []
        for cat in X:
            c = Counter(cat)
            if self.features:
                d = {k:c[k] for k in self.features}
                cat_list.append(d)
            else:
                cat_list.append(c)
        return cat_list

    def _construct_neighborhood_df(self):
        mean_lat = self.business_df.groupby('neighborhood').latitude.mean()
        mean_lon = self.business_df.groupby('neighborhood').longitude.mean()
        cat_concat = self.business_df.groupby('neighborhood').categories.sum()
        mean_dollar= self.business_df.groupby('neighborhood').dollars.mean()
        mean_stars= self.business_df.groupby('neighborhood').stars.mean()
        df = pd.DataFrame({ 'latitude': mean_lat, \
                            'longitude': mean_lon,\
                            'categories':cat_concat,\
                            'dollar': mean_dollar,\
                            'stars': mean_stars})
        int_id = df.index.map(lambda x: int(x.split('_')[1]))
        df['int_id'] = int_id
        df['name'] = [ self.neighborhoods[i] for i in int_id]
        count = self.all_counts[self.city]
        df['count'] = [count[i] for i in int_id]
        df['count'].fillna(df['count'].mean(),inplace=True)
        df['dollar'].fillna(df['dollar'].mean(),inplace=True)
        df['cat_counters'] = self._get_cat_counters(df.categories)
        return df

    def nearest_neighborhood(self,latlon=None,address=None):
        if address:
            lat,lon = googleGeocoding(address)
        grid_points = zip(self.neighborhood_df.latitude,self.neighborhood_df.longitude)
        distances = np.array([distance((lat,lon),gp) for gp in grid_points])
        id_min = distances.argmin()
        return id_min

    def neighborhood_polygon(self,nid):
        p = zip(self.neighborhood_df.latitude, self.neighborhood_df.longitude)
        poly = MultiPoint(p).convex_hull
        px,py = poly.exterior.xy
        output_points =[{'lat':x, 'lng':y} for x,y in zip(px,py)]
        return output_points

    def neighborhood_containing_point(self,latlon=None,address=None):
        nid = self.nearest_neighborhood(latlon=latlon, address=address)
        return self.neighborhood_polygon(nid)

    def _construct_feature_matrix(self):
        #ipdb.set_trace()
        v = DictVectorizer()
        t = TfidfTransformer()
        catX = v.fit_transform(self.neighborhood_df['cat_counters'])
        catX = t.fit_transform(catX).toarray()
        self.features = v.feature_names_
        otherX = self.neighborhood_df[['dollar','stars','count']].values
        otherX = otherX - otherX.mean(axis=0)
        normX  = norm(otherX,axis=0)
        otherX = otherX/norm(otherX,axis=0)
        otherX[np.isnan(otherX)] = 0.0
        return np.hstack((catX,otherX))

    def find_similar_to_ref(self,input_vector,num_results=5):
        assert(self.X.shape[1] == input_vector.shape[0])
        sims = cosine_similarity(self.X,input_vector)[:,0]
        ind_sort = sims.argsort()[:-1:-1]
        return ind_sort[:num_results]

    def getVector(self,neighborhood_id):
        return self.X[neighborhood_id,:]

    def _rand_split(self):
        N = len(self.business_df)
        rowsA = np.random.rand(N) > 0.5
        sampleA = self.business_df[rowsA].copy()
        sampleB = self.business_df[~rowsA].copy()
        cityA = CityNeighborhood(city = self.city, business_df=sampleA, \
                            features = self.features)
        cityB = CityNeighborhood(city = self.city, business_df=sampleB, \
                            features = self.features)
        return cityA,cityB

    def self_validate(self,Niterations=5,feature_func= None):
        outcomes = []
        N = len(self.neighborhood_df)
        for i in range(Niterations):
            c1, c2 = self._rand_split()
            if feature_func == None:
                X1 = c1.X
                X2 = c2.X
            else:
                X1 = feature_func(c1)
                X2 = feature_func(c2)
            sim_split = cosine_similarity(X1,X2)
            outcome = (sim_split.argmax(axis=0) == np.arange(N)).mean()
            outcomes.append(outcome)
        return np.mean(outcomes)

    def pickle(self,filename):
        with open(filename,'wb') as oo:
            cPickle.dump(self,oo)


def join(cityA,cityB):
    pass


def unpickle(filename):
    with open(filename,'rb') as oo:
        city = cPickle.load(oo)
    return city
