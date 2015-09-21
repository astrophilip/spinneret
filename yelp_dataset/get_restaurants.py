import urllib2
import bs4
from bs4 import BeautifulSoup
import re
import json

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

def readparse(inputurl):
    # return bs4 parsed html page
    rsp = urllib2.urlopen(inputurl)
    html = rsp.read()
    prsd = BeautifulSoup(html)
    return prsd

def parse_latlon(html):
    tmp = html.find_all("script")

    # get the relevant tag manually
    ss = tmp[-6]

    # all text between and "markers:" and  "top_biz_bounds"
    otxt = ss.contents[0]
    strt = "markers"
    endt = "top_biz_bounds"
    strtndx = otxt.find(strt)
    endndx = otxt.find(endt)
    bzlst=otxt[strtndx+len(strt)+3:endndx-3]
    yelp_dict = json.loads(bzlst)
    return yelp_dict

neighborhoods = ['p:MA:Boston::Back_Bay']

def yelp_dog_scrapy_proto_philip(neighborhood):
    # scrapes yelp results page for business information in map script
    tst = "http://www.yelp.com/search?&l=" + neighborhood + "&start=0"
    html = readparse(tst)
    pgntn = html.find_all("span",{"class":"pagination-results-window"})[0].text

    m = re.search(r'of\s(.+)',pgntn)
    N = int(m.group(1))

    max_search = 20
    maxN = min(N,max_search)
    biz_dict = {}
    for start_page in range(0,maxN,10):
        # get all script tags
        print start_page
        tst = "http://www.yelp.com/search?&l=" + neighborhood + "&start=" + str(start_page)
        html = readparse(tst)
        latlon_dict = parse_latlon(html)
        temp_dict = clean_latlon_dict(latlon_dict)
        biz_dict.update(temp_dict)
    return N, biz_dict
