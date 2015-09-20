import pandas as pd
import sqlalchemy
from sqlalchemy import VARCHAR, TEXT


def _yelp_to_str(filename):
    with open(filename, 'rb') as f:
        data = f.readlines()
    # remove the trailing "\n" from each line
    data = map(lambda x: x.rstrip(), data)
    data_json_str = "[" + ','.join(data) + "]"
    return data_json_str

def create_df_from_user_json():
    # read the entire file into a pandas dataframe
    filename = 'yelp_academic_dataset_user.json'
    data_json_str = _yelp_to_str(filename)

    # now, load it into pandas
    df = pd.read_json(data_json_str)
    return df

def create_df_from_review_json():
    # read the entire file into a pandas dataframe
    filename = 'yelp_academic_dataset_review.json'
    with open(filename, 'rb') as f:
        data = f.readlines()
    # remove the trailing "\n" from each line
    data = map(lambda x: x.rstrip(), data)
    L = len(data)
    data1=data[:L//2] #I have to split into 2 cuz pandas bit it
    data2=data[L//2:]
    data_json_str1 = "[" + ','.join(data1) + "]"
    #data_json_str2 = "[" + ','.join(data2) + "]"
    df1 = pd.read_json(data_json_str1)
    #df2 = pd.read_json(data_json_str2)
    #df = pd.concat([df1,df2])
    return df1

def create_df_from_business_json():
    # read the entire file into a pandas dataframe
    filename = 'yelp_academic_dataset_business.json'
    data_json_str = _yelp_to_str(filename)

    df = pd.read_json(data_json_str)
    columns = ['business_id', 'categories', 'city', 'hours', 'latitude', \
        'longitude', 'full_address','name', 'neighborhoods', 'review_count', 'stars']
    df = df[columns]
    df.columns.values[-1]= 'Bstars'
    return df

def create_df_from_tip_json():
    # read the entire file into a pandas dataframe
    filename = 'yelp_academic_dataset_tip.json'
    data_json_str = _yelp_to_str(filename)

    df = pd.read_json(data_json_str)
    return df

def create_df_from_checkin_json():
    # read the entire file into a pandas dataframe
    filename = 'yelp_academic_dataset_checkin.json'
    data_json_str = _yelp_to_str(filename)

    df = pd.read_json(data_json_str)
    return df

def flatten_df(df,column,new_column_name=None):
    assert(len(df.columns) > 1)
    other_columns = list(df.columns[df.columns != column])
    if len(other_columns) == 1:
        other_columns = other_columns[0]
    data = [list(y[other_columns])+[x] for i, y in df.iterrows() for x in y[column]]

    index= [i for i, y in df.iterrows() for x in y[column]]
    if new_column_name != None:
        new_columns = list(other_columns) + [new_column_name]
    else:
        new_columns = list(other_columns) + [column]
    newdf = pd.DataFrame(data=data,columns=new_columns,index=index)
    newdf.index.name = df.index.name
    return newdf


def construct_bus_db():
    engine = sqlalchemy.create_engine("mysql+pymysql://root@localhost/yelp?charset=utf8")
    dfB = create_df_from_business_json()
    columns =['business_id','city','latitude','longitude','name','Bstars','review_count']
    dfB_for_sql = dfB[columns].copy()

    to_recast = dfB_for_sql.dtypes[dfB_for_sql.dtypes == 'object'].index
    mapping_dict = {k: VARCHAR(63) for k in to_recast}
    mapping_dict['name'] = TEXT
    mapping_dict['address']

    dfB_for_sql.to_sql('business',engine,dtype=mapping_dict)

    B = dfB[['business_id','categories']]

    dfbus_cat = flatten_df(B,'categories',new_column_name= 'category')
    to_recast = dfbus_cat.dtypes[dfbus_cat.dtypes == 'object'].index
    mapping_dict = {k: VARCHAR(63) for k in to_recast}
    mapping_dict['category'] = TEXT
    dfbus_cat.to_sql('bus_cat',engine,dtype=mapping_dict)


def construct_review_db():
    engine = sqlalchemy.create_engine("mysql+pymysql://root@localhost/yelp?charset=utf8")
    dfR = create_df_from_review_json()
    columns = ['business_id', 'review_id', 'stars', 'text','user_id']
    dfR_tosql = dfR[columns].copy()

    to_recast = dfR.dtypes[dfR.dtypes == 'object'].index
    mapping_dict = {k: VARCHAR(63) for k in to_recast}
    mapping_dict['text']= TEXT
    dfR_tosql.to_sql('reviews', engine,dtype=mapping_dict)
