import numpy as np
import pandas as pd
import ipdb

REARTH = 3959.0 #miles
STEP = 0.3 #miles
RAD = np.radians(1)

def cartesian_prod(x,y):
    return np.array([np.tile(x,len(y)),np.repeat(y,len(x))]).T


class CityNeighborhoods(object):
    _bounds= {'phoenix':[33.0,34.0,-112.6,-111.4]}
    _lats = {'phoenix' : 33.4}

    def __init__(self,city='phoenix',business_df=None):
        if business_df is None:
            raise Exception('Must supply business_df')
        self.city = city
        #ipdb.set_trace()

        bounds = self._bounds[city]
        cond1 = (business_df.latitude > bounds[0]) &  \
                (business_df.latitude < bounds[1])
        cond2 = (business_df.longitude > bounds[2]) &  \
                (business_df.longitude < bounds[3])

        self.business_df = business_df[cond1 & cond2]
        self.grid_df = self.construct_grid_df()
        self.cat_counter_list = self.construct_grid_cat_counter_list()


    def find_estab(self,lat,lon, dist):
        # dist in miles
        dlat = dist/REARTH/RAD
        dlon = dist/REARTH/RAD/np.cos(RAD*lat)
        ids =  (abs(self.business_df.latitude -lat) < dlat ) & \
                (abs(self.business_df.longitude -lon) < dlon )
        return list(self.business_df.index[ids])

    def _setup_grid(self):
        print 'setting up grid'
        bounds = self._bounds[self.city]
        city_lat = self._lats[self.city]
        dlat = STEP/REARTH/RAD
        dlon = STEP/REARTH/RAD/np.cos(RAD*city_lat)
        lats = np.arange(bounds[0],bounds[1],dlat)
        lons = np.arange(bounds[2],bounds[3],dlon)
        z = cartesian_prod(lats, lons)
        return z

    def construct_grid_df(self):
        print 'initializing grid_df'
        z = self._setup_grid()
        latitude, longitude = z[:,0], z[:,1]
        df = pd.DataFrame({'latitude': latitude,'longitude': longitude})
        estab_count = []
        estab_list = []
        for lat,lon in zip(latitude,longitude):
            el = self.find_estab(lat,lon,STEP)
            estab_count.append(len(el))
            estab_list.append(el)
        df['estab_count']=estab_count
        df['estab_list']= estab_list
        df = df[df.estab_count > 10]
        df.reset_index(drop=True,inplace=True)
        df.index.name = 'grid_id'
        df['latlon'] = zip(df['latitude'],df['longitude'])
        return df

    def construct_grid_cat_counter(self,estab_list):
        cat_counter = Counter()
        for i in estab_list:
            cat_counter.update(self.business_df.ix[i,'categories'])
        return cat_counter

    def construct_grid_cat_counter_list(self):
        print 'augmenting grid_df'
        #takes a list of cat_counters
        counter_list = []
        for estab_list in self.grid_df.estab_list:
            cat_count = self.construct_grid_cat_counter(self.business_df,
                                    estab_list)
            counter_list.append(cat_count)
        self.grid_df['cat_counter'] = counter_list
