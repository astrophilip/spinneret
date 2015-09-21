import numpy as np
import pandas as pd
import ipdb

REARTH = 3959.0 #miles
STEP = 0.3 #miles
RAD = np.radians(1)

def cartesian_prod(x,y):
    return np.array([np.tile(x,len(y)),np.repeat(y,len(x))]).T


class CityNeighborhoods(object):
    _bounds= {'Phoenix':[33.0,34.0,-112.6,-111.4]}
    _lats = {'Phoenix' : 33.4}

    def __init__(self,city='Phoenix',business_df=None):
        if business_df is None:
            raise Exception('Must supply business_df')
        self.Name = city
        bounds = _bounds[city]
        cond1 = (business_df.latitude > bounds[0]) &  \
                (business_df.latitude < bounds[1])
        cond2 = (business_df.longitude > bounds[2]) &  \
                (business_df.longitude < bounds[3])
        ipdb.set_trace()

        self.business_df = business_df[cond1 & cond2]
        self.grid_df = construct_grid_df()

    def find_estab(self,lat,lon, dist):
        # dist in miles
        dlat = dist/REARTH/RAD
        dlon = dist/REARTH/RAD/np.cos(RAD*lat)
        ids =  (abs(self.business_df.latitude -lat) < dlat ) & \
                (abs(self.business_df.longitude -lon) < dlon )
        return list(self.business_df.index[ids])

    def _setup_grid(self):
        bounds = _bounds[self.city]
        city_lat = _lats[self.city]
        dlat = STEP/REARTH/RAD
        dlon = STEP/REARTH/RAD/np.cos(RAD*city_lat)
        lats = np.arange(_bounds[0],_bounds[1],dlat)
        lons = np.arange(_bounds[2],_bounds[3],dlon)
        z = cartesian_prod(lats, lons)
        return z

    def construct_grid_df(self):
        z = _setup_grid(self)
        latitude, longitude = z[:,0], z[:,1]
        df = pd.DataFrame({'latitude': latitude,'longitude': longitude})
        estab_count = []
        estab_list = []
        for lat,lon in zip(latitude,longitude):
            el = find_estab(lat,lon,STEP,self.business_df)
            estab_count.append(len(el))
            estab_list.append(el)
        df['estab_count']=estab_count
        df['estab_list']= estab_list
        df = df[df.estab_count > 10]
        df.reset_index(drop=True,inplace=True)
        df.index.name = 'grid_id'
        df['latlon'] = zip(df['latitude'],df['longitude'])
        return df
