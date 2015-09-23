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

NEIGHBORHOODS = gn.neighborhoods
COUNTS = gn.counts

REARTH = 3959.0 #miles
STEP = 0.3 #miles
RAD = np.radians(1)

def cartesian_prod(x,y):
    return np.array([np.tile(x,len(y)),np.repeat(y,len(x))]).T


class CityNeighborhood(object):
    '''
    Collection of Neighborhoods with methods to populate neighborhood
    feautures.
    Provides methods to compare similarities of neighborhoods
    '''
    def __init__(self,city='BOS',business_df=None, _features = None):
        if business_df is None:
            business_df = ydf.create_bus_df_from_neighborhoods(city)

        self.city = city
        self._features = _features
        #ipdb.set_trace()

        self.neighborhoods = NEIGHBORHOODS[city]
        self.nids = range(len(NEIGHBORHOODS))
        self.business_df = business_df[business_df.city == city]
        self.neighborhood_df = self._construct_neighborhood_df()
        self.X = self._construct_feature_matrix()
        #self.cat_counter_list = self.construct_neighborhood_cat_counter_list()

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
            if self._features:
                d = {k:c[k] for k in self._features}
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
        count = COUNTS[self.city]
        df['count'] = [count[i] for i in int_id]
        df['cat_counters'] = self._get_cat_counters(df.categories)
        return df

    def _construct_feature_matrix(self):
        #ipdb.set_trace()
        v = DictVectorizer()
        t = TfidfTransformer()
        catX = v.fit_transform(self.neighborhood_df['cat_counters'])
        catX = t.fit_transform(catX).toarray()
        self._features = v.feature_names_
        otherX = self.neighborhood_df[['dollar','stars','count']].values
        otherX = otherX - otherX.mean(axis=0)
        otherX = otherX/norm(otherX,axis=0)
        return np.hstack((catX,otherX))

    def find_similar_to_ref(self,input_vector,num_results=5):
        assert(self.X.shape[1] == input_vector.shape[0])
        sims = cosine_similarity(self.X,input_vector)[:,0]
        ind_sort = sims.argsort()[:-1:-1]
        return ind_sort[:num_results]


    def _rand_split(self):
        N = len(self.business_df)
        rowsA = np.random.rand(N) > 0.5
        sampleA = self.business_df[rowsA].copy()
        sampleB = self.business_df[~rowsA].copy()
        cityA = CityNeighborhood(city = self.city, business_df=sampleA, \
                            _features = self._features)
        cityB = CityNeighborhood(city = self.city, business_df=sampleB, \
                            _features = self._features)
        return cityA,cityB

    def self_validate(self,Niterations=5):
        outcomes = []
        N = len(self.neighborhood_df)
        for i in range(Niterations):
            c1, c2 = self._rand_split()
            sim_split = cosine_similarity(c1.X,c2.X)
            outcome.append(sim_split.argmax(axis=0) == np.arange(N).mean())
        return np.mean(outcomes)

def join(cityA,cityB):
    pass
