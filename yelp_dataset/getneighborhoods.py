import urllib2
import requests
import bs4
from bs4 import BeautifulSoup
import re
import json
import ipdb
import random
import time

neighborhoods = \
['Allston/Brighton' , 'Arlington_Center' , 'Arlington_Heights','Back_Bay', \
'Beacon_Hill','Brookline_Village','Central_Square','Charlestown','Chinatown',\
'Coolidge_Corner','Davis_Square','Dorchester','Downtown','Dudley_Square',\
'East_Arlington','East_Boston','East_Cambridge','Egleston_Square','Fenway',\
'Fields_Corner','Financial_District', \
'Harvard_Square','Huron_Village' , 'Hyde_Park','Inman_Square','Jamaica_Plain', \
'Kendall_Square/MIT','Leather_District','Mattapan','Mattapan_Square',\
'Mission_Hill','North_Cambridge','North_End','Porter_Square','Roslindale', \
'Roslindale_Village','South_Boston','South_End','Teele_Square', \
'Uphams_Corner','Waterfront','West_Roxbury','West_Roxbury_Center','Winthrop']


def readparse(s,inputurl):
    # return bs4 parsed html page
    html = s.get(inputurl).text
    prsd = BeautifulSoup(html)
    return prsd

def parse_latlon(html):
    otxt = html.text
    strt = '"markers": {"'
    endt = "top_biz_bounds"
    strtndx = otxt.find(strt)
    endndx = otxt.find(endt)
    bzlst=otxt[strtndx+11:endndx-3]
    yelp_dict = json.loads(bzlst)
    return yelp_dict

def clean_yelp_biz_dict(d):
    d_new = {}
    d_new['latitude'] = d['location']['latitude']
    d_new['longitude']= d['location']['longitude']
    return d['url'],d_new

def clean_latlon_dict(d):
    d_updated = {}
    for key in d.keys():
        biz_name,biz_dict = clean_yelp_biz_dict(d[key])
        d_updated[biz_name] = biz_dict
    return d_updated

def clean_dirty_cat(dirty_cat):
    Ncat = len(dirty_cat)
    if Ncat ==0:
        cats=[]
    else:
        cats = [c.text for c in dirty_cat]
    return cats

def parse_biz_names(html):
    dirty_names = html.findAll('a',{'class':"biz-name"})
    return map(lambda x: x['href'], dirty_names)

def parse_cats(html):
    dirty_cats= html.find_all('span',{'class':"category-str-list"})
    dirty_cats= map(lambda x: x.contents[1::2],dirty_cats)
    return [clean_dirty_cat(dc) for dc in dirty_cats]

def parse_dollars(html):
    dirty_dollars = html.findAll('span',{'class':'business-attribute price-range'})
    dollars= {}
    for d in dirty_dollars:
        item = d.find_parents(limit=3)[2]
        biz_name = parse_biz_names(item)[0]
        dollars[biz_name] = len(d.contents[0])
    return dollars

def parse_ratings(html):
    dirty_ratings = html.findAll('img',{'class':'offscreen','height':'303'})
    ratings= {}
    for r in dirty_ratings:
        item = r.find_parents(limit=4)[3]
        biz_name = parse_biz_names(item)[0]
        ratings[biz_name] = len(r.contents[0])
    return ratings



def yelp_by_neighborhood(neighborhood,max_search=1000,sleep=True):
    # scrapes yelp results page for business information in map script
    tst = "http://www.yelp.com/search?&l=p:MA:Boston::" + neighborhood + "&start=0"
    s = requests.Session()
    html = readparse(s, tst)
    pgntn = html.find_all("span",{"class":"pagination-results-window"})[0].text

    m = re.search(r'of\s(.+)',pgntn)
    N = int(m.group(1))
    print N
    maxN = min(N,max_search)
    biz_dict = {}
    for start_page in range(0,maxN,10):
        # get all script tags
        print start_page
        tst = "http://www.yelp.com/search?&l=p:MA:Boston::" + neighborhood + "&start=" + str(start_page)
        html = readparse(s, tst)

        latlon_dict = parse_latlon(html)
        names = parse_biz_names(html)
        cats = parse_cats(html)
        dollars = parse_dollars(html)
        ratings = parse_ratings(html)

        temp_dict = clean_latlon_dict(latlon_dict)
        for n,c in zip(names,cats):
            temp_dict[n]['categories']= c

        for r in ratings.keys():
            temp_dict[n]['stars']= r

        for n in dollars.keys():
            temp_dict[n]['dollars'] = dollars[n]

        biz_dict.update(temp_dict)
        if sleep:
            time.sleep(random.uniform(1,4))
    return N, biz_dict

def record_neighborhood(n_id,biz_dict):
    filename = 'neighborhoods/BOS_'+str(n_id)+'.json'
    with open(filename,'w') as f:
        json.dump(biz_dict,f)

def parse_all_neighborhoods(neighborhoods):
    counts = []
    for nid,neighborhood in enumerate(neighborhoods):
        N, biz_dict = yelp_by_neighborhood(neighborhood)
        record_neighborhood(nid, biz_dict)
        counts.append(N)
    print counts
