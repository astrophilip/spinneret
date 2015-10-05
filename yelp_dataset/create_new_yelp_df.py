import pandas as pd
import sqlalchemy
from sqlalchemy import VARCHAR, TEXT
import os
import re

def process_json(f):
    nid = re.search(r"(\w\w\w_\d+).json",f).group(1)
    df = pd.read_json(f,orient='index')
    df['neighborhood'] = nid
    print nid
    return df

def create_bus_df_from_neighborhoods(city='BOS'):
    # read the entire file into a pandas dataframe
    dirname = os.path.join(os.path.dirname(__file__),"neighborhoods/")
    command = 'ls '+dirname+city+'*'
    with os.popen(command) as com:
        files_dirty = com.readlines()
        files = [f.strip() for f in files_dirty]

    frame_gen = (process_json(f) for f in files)
    df = pd.concat(frame_gen)
    df = df[df.categories.notnull()]
    df['city']=city
    return df

def create_busdf_for_sql(city='BOS'):
    # read the entire file into a pandas dataframe
    dirname = os.path.join(os.path.dirname(__file__),"neighborhoods/")
    command = 'ls '+dirname+city+'*'
    with os.popen(command) as com:
        files_dirty = com.readlines()
        files = [f.strip() for f in files_dirty]

    frame_gen = (process_json(f) for f in files)
    df = pd.concat(frame_gen)
    df['city']=city
    return df
