import numpy as np
import pandas as pd
from collections import Counter
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.stats import rankdata
import ipdb
import getneighborhoods as gn
import create_new_yelp_df as ydf
from numpy.linalg import norm
from geopy.distance import distance
from shapely.geometry import MultiPoint
import cPickle
import json, urllib

NEIGHBORHOODS = gn.clean_neighborhoods
COUNTS = gn.counts

REARTH = 3959.0 #miles
STEP = 0.3 #miles
RAD = np.radians(1)
CITY_NAMES = ['Boston', 'NYC']

def googleGeocoding(address):
    """This function takes an address and returns the latitude and longitude
    from the Google geocoding API."""
    baseURL = 'http://maps.googleapis.com/maps/api/geocode/json?'
    geocodeURL = baseURL + 'address=' + address #+'&key=' + key
    geocode = json.loads(urllib.urlopen(geocodeURL).read())
    lat = geocode['results'][0]['geometry']['location']['lat']
    lon = geocode['results'][0]['geometry']['location']['lng']
    return lat, lon

def add_mean_latlon(x):
    x['mlat'] = x.latitude.mean()
    x['mlon'] = x.longitude.mean()
    return x

def hdistance(a, b):
    dlat = np.radians(a[:,0]) - np.radians(b[:,0])
    dlon = np.radians(a[:,1]) - np.radians(b[:,1])
    aa = np.square(np.sin(dlat/2.0)) + np.cos(np.radians(b[:,0])) * np.cos(np.radians(a[:,0])) * np.square(np.sin(dlon/2.0))
    d = REARTH*2 * np.arcsin(np.minimum(np.sqrt(aa), np.repeat(1, len(aa))))
    return d

def clip_func(x):
    y = hdistance(x[['latitude','longitude']].values,x[['mlat','mlon']].values)
    return y < 4*np.mean(y)
def clean_business_df(df,k=10):
    df = df.copy()
    for i in range(k):
        df = df.groupby('neighborhood').apply(add_mean_latlon)
        df = df[clip_func(df)]
    return df

class CityNeighborhood(object):
    '''
    Collection of Neighborhoods with methods to populate neighborhood
    feautures.
    Provides methods to compare similarities of neighborhoods
    '''
    all_neighborhoods = NEIGHBORHOODS
    all_counts = COUNTS
    def __init__(self,city='BOS',business_df=None,
        features = None, feature_func=None):
        if business_df is None:
            business_df = ydf.create_bus_df_from_neighborhoods(city)

        self.city = city
        self.features = features
        self.topic_model = None
        #ipdb.set_trace()

        self.neighborhoods = self.all_neighborhoods[city]
        self._neighborhood_index = self._invert_neighborhoods()
        self.nids = range(len(self.neighborhoods))
        if not city == 'JOINED':
            business_df = business_df[business_df.city == city]

        self.business_df = clean_business_df(business_df)
        self.neighborhood_df = self._construct_neighborhood_df()
        if feature_func is None:
            self.X = self._construct_feature_matrix()
        else:
            self.X = feature_func(self)
        self.cat_pmi = self.pmi()

    def _invert_neighborhoods(self):
        return {v:i for i,v in enumerate(self.neighborhoods) }

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
        df = df.sort('int_id')
        return df

    def nearest_neighborhood(self,latlon=None,address=None):
        if address:
            lat,lon = googleGeocoding(address)
        grid_points = zip(self.neighborhood_df.latitude,self.neighborhood_df.longitude)
        distances = np.array([distance(latlon,gp) for gp in grid_points])
        id_min = distances.argmin()
        return id_min

    def neighborhood_polygon(self,nid):
        ind  = self.neighborhood_df.index[nid]
        df = self.business_df[self.business_df.neighborhood == ind]
        p = zip(df.latitude, df.longitude)
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
        catX = catX.toarray()#t.fit_transform(catX).toarray()
        self.catX = catX
        catX = catX/norm(catX,axis=0)
        catX[np.isnan(catX)] = 0.0
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
        ind_sort = sims.argsort()[:-2:-1]
        return ind_sort[:num_results]

    def find_diff_from_ref(self,input_vector,num_results=5):
        assert(self.X.shape[1] == input_vector.shape[0])
        sims = cosine_similarity(self.X,input_vector)[:,0]
        ind_sort = sims.argsort()[-2:]
        return ind_sort[:num_results]

    def getVector(self,neighborhood_id):
        return self.X[neighborhood_id,:]

    def getCountVector(self,neighborhood_id):
        return self.catX[neighborhood_id,:].astype(int)

    def pmi(self):
        catXb = self.catX + 1
        p_xy = catXb/catXb.sum()
        p_x = catXb.sum(axis=1).reshape(-1,1)/catXb.sum()
        p_y = catXb.sum(axis=0)/catXb.sum().reshape(-1,1)
        return np.log(p_xy/p_x/p_y)

    def getKeyWords(self,input_CountVector,num_results=5):
        model.transform(input_CountVector)
        key_words = np.argsort(X[sim_id,:] - X[diff_id,:])[::-1]
        N = min(len(key_words),num_results)
        print max(key_words)
        print len(self.features)
        return  [self.features[kw] for kw in key_words[:N]]

    def set_topic_model(self,model):
        self.topic_model = model

    def _rand_split(self):
        # splits each neighborhood on a random axis
        N = len(self.business_df)
        rowsA = self.business_df.latitude > self.business_df.mlat
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
            outcome = (sim_split.argmax(axis=0) == np.arange(N) ).mean()
            sucesses =0

            outcomes.append(outcome)
        ipdb.set_trace()
        return np.mean(outcomes)

    def pickle(self,filename):
        with open(filename,'wb') as oo:
            cPickle.dump(self,oo)

    def index_lookup(self,neighborhood):
        if not self._neighborhood_index.has_key(neighborhood):
            ret = None
        else:
            ret = self._neighborhood_index[neighborhood]
        return ret



def join(cityA,cityB):
    business_df = pd.concat([cityA.business_df,cityB.business_df])
    cityC = CityNeighborhood('JOINED',business_df=business_df,
                features=cityA.features)
    return cityC


def unpickle(filename):
    with open(filename,'rb') as oo:
        city = cPickle.load(oo)
    return city


def setup():
    bos = CityNeighborhood('BOS')
    nyc = CityNeighborhood("NYC",features= bos.features)
    bos.pickle('bos.pickle')
    nyc.pickle('nyc.pickle')


def tf_idf_features(self):
    #ipdb.set_trace()
    v = DictVectorizer()
    t = TfidfTransformer()
    catX = v.fit_transform(self.neighborhood_df['cat_counters'])
    catX = t.fit_transform(catX).toarray()
    self.features = v.feature_names_
    return catX

def tf_idf_features2(self):
    #ipdb.set_trace()
    v = DictVectorizer()
    t = TfidfTransformer()
    catX = v.fit_transform(self.neighborhood_df['cat_counters'])
    catX = t.fit_transform(catX).toarray()
    self.features = v.feature_names_
    catX = catX/norm(catX,axis=0)
    catX[np.isnan(catX)] = 0.0
    return catX

def fit_topic_model(city):
    if not city.city == 'JOINED':
        raise AttributeError('Topics must be generated from entire data set. Use joined city')
    v = DictVectorizer()
    catX = v.fit_transform(city.neighborhood_df['cat_counters'])
    model = lda.LDA(n_topics= 20, n_iter= 5000, random_state=1)
    model.fit_transform(catX)
    return model

def topic_model_features(self):
    pass


def test(bos_address,ff=None):
    """
    give the address in first city
    print the neighborhood in 2nd city
    """

    ref_latitude, ref_longitude = googleGeocoding(bos_address)
    bos = CityNeighborhood('BOS',business_df = pd.read_pickle('bosdf.pickle'),
                feature_func= ff)
    nyc = CityNeighborhood("NYC",business_df = pd.read_pickle('nycdf.pickle'),
                feature_func= ff, features= bos.features)

    input_nid = bos.nearest_neighborhood(latlon= (ref_latitude,ref_longitude))
    home_name = bos.neighborhood_df.ix[input_nid,'name']
    home_neighborhood = bos.getVector(input_nid)

    print input_nid, home_name
    output_nid = nyc.find_similar_to_ref(home_neighborhood,num_results=1)[0]
    away_neighborhood = nyc.getVector(input_nid)
    away_name         = nyc.neighborhood_df.ix[output_nid,'name']
    print output_nid, away_name
    print nyc.self_validate(1,feature_func=ff)
    return bos,nyc

def getKeywords(cityA,cityB,nid_A,nid_B):
    features = cityA.features
    Aranks = rankdata(cityA.cat_pmi[nid_A])
    Branks = rankdata(cityB.cat_pmi[nid_B])
    good_features = (Aranks+Branks).argsort()[::-1]
    weights = np.sort(len(features)*2.0 - (Aranks+Branks))[::-1][:20]
    good_words = [features[i] for i in good_features[:20]]
    return good_words,weights


##chinatown boston
##backbay boston
##fenway boston
##davis square
##harvard square cambridge
##
