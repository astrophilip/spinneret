import urllib2
import requests
import bs4
from bs4 import BeautifulSoup
import re
import json
import ipdb
import random
import time

neighborhoods = { 'BOS' :\
['Allston/Brighton' , 'Arlington_Center' , 'Arlington_Heights','Back_Bay', \
'Beacon_Hill','Brookline_Village','Central_Square','Charlestown','Chinatown',\
'Coolidge_Corner','Davis_Square','Dorchester','Downtown','Dudley_Square',\
'East_Arlington','East_Boston','East_Cambridge','Egleston_Square','Fenway',\
'Fields_Corner','Financial_District', \
'Harvard_Square','Huron_Village' , 'Hyde_Park','Inman_Square','Jamaica_Plain',\
'Kendall_Square/MIT','Leather_District','Mattapan','Mattapan_Square',\
'Mission_Hill','North_Cambridge','North_End','Porter_Square','Roslindale', \
'Roslindale_Village','South_Boston','South_End','Teele_Square', \
'Uphams_Corner','Waterfront','West_Roxbury','West_Roxbury_Center','Winthrop'],\
    'NYC':\
    [ 'Brooklyn:Bath_Beach', \
 'Brooklyn:Bay_Ridge',\
 'Brooklyn:Bedford_Stuyvesant',\
 'Brooklyn:Bensonhurst',\
 'Brooklyn:Bergen_Beach',\
 'Brooklyn:Boerum_Hill',\
 'Brooklyn:Borough_Park',\
 'Brooklyn:Brighton_Beach',\
 'Brooklyn:Brooklyn_Heights',\
 'Brooklyn:Brownsville',\
 'Brooklyn:Bushwick',\
 'Brooklyn:Canarsie',\
 'Brooklyn:Carroll_Gardens',\
 'Brooklyn:City_Line',\
 'Brooklyn:Clinton_Hill',\
 'Brooklyn:Cobble_Hill',\
 'Brooklyn:Columbia_Street_Waterfront_District',\
 'Brooklyn:Coney_Island',\
 'Brooklyn:Crown_Heights',\
 'Brooklyn:Cypress_Hills',\
 'Brooklyn:DUMBO',\
 'Brooklyn:Ditmas_Park',\
 'Brooklyn:Downtown_Brooklyn',\
 'Brooklyn:Dyker_Heights',\
 'Brooklyn:East_Flatbush',\
 'Brooklyn:East_New_York',\
 'Brooklyn:East_Williamsburg',\
 'Brooklyn:Flatbush',\
 'Brooklyn:Flatlands',\
 'Brooklyn:Fort_Greene',\
 'Brooklyn:Fort_Hamilton',\
 'Brooklyn:Georgetown',\
 'Brooklyn:Gerritson_Beach',\
 'Brooklyn:Gowanus',\
 'Brooklyn:Gravesend',\
 'Brooklyn:Greenpoint',\
 'Brooklyn:Highland_Park',\
 'Brooklyn:Kensington',\
 'Brooklyn:Manhattan_Beach',\
 'Brooklyn:Marine_Park',\
 'Brooklyn:Midwood',\
 'Brooklyn:Mill_Basin',\
 'Brooklyn:Mill_Island',\
 'Brooklyn:New_Lots',\
 'Brooklyn:Ocean_Hill',\
 'Brooklyn:Ocean_Parkway',\
 'Brooklyn:Paedergat_Basin',\
 'Brooklyn:Park_Slope',\
 'Brooklyn:Prospect_Heights',\
 'Brooklyn:Prospect_Lefferts_Gardens',\
 'Brooklyn:Prospect_Park',\
 'Brooklyn:Red_Hook',\
 'Brooklyn:Remsen_Village',\
 'Brooklyn:Sea_Gate',\
 'Brooklyn:Sheepshead_Bay',\
 'Brooklyn:South_Slope',\
 'Brooklyn:South_Williamsburg',\
 'Brooklyn:Spring_Creek',\
 'Brooklyn:Starret_City',\
 'Brooklyn:Sunset_Park',\
 'Brooklyn:Vinegar_Hill',\
 'Brooklyn:Weeksville',\
 'Brooklyn:Williamsburg_-_North_Side',\
 'Brooklyn:Williamsburg_-_South_Side',\
 'Brooklyn:Windsor_Terrace',\
 'Brooklyn:Wingate',\
 'Manhattan:Alphabet_City',\
 'Manhattan:Battery_Park',\
 'Manhattan:Central_Park',\
 'Manhattan:Chelsea',\
 'Manhattan:Chinatown',\
 'Manhattan:Civic_Center',\
 'Manhattan:East_Harlem',\
 'Manhattan:East_Village',\
 'Manhattan:Financial_District',\
 'Manhattan:Flatiron',\
 'Manhattan:Gramercy',\
 'Manhattan:Greenwich_Village',\
 'Manhattan:Harlem',\
 "Manhattan:Hell's_Kitchen",\
 'Manhattan:Inwood',\
 'Manhattan:Kips_Bay',\
 'Manhattan:Koreatown',\
 'Manhattan:Little_Italy',\
 'Manhattan:Lower_East_Side',\
 'Manhattan:Manhattan_Valley',\
 'Manhattan:Marble_Hill',\
 'Manhattan:Meatpacking_District',\
 'Manhattan:Midtown_East',\
 'Manhattan:Midtown_West',\
 'Manhattan:Morningside_Heights',\
 'Manhattan:Murray_Hill',\
 'Manhattan:NoHo',\
 'Manhattan:Nolita',\
 'Manhattan:Roosevelt_Island',\
 'Manhattan:SoHo',\
 'Manhattan:South_Street_Seaport',\
 'Manhattan:South_Village',\
 'Manhattan:Stuyvesant_Town',\
 'Manhattan:Theater_District',\
 'Manhattan:TriBeCa',\
 'Manhattan:Two_Bridges',\
 'Manhattan:Union_Square',\
 'Manhattan:Upper_East_Side',\
 'Manhattan:Upper_West_Side',\
 'Manhattan:Washington_Heights',\
 'Manhattan:West_Village',\
 'Manhattan:Yorkville',\
 'Queens:Arverne',\
 'Queens:Astoria',\
 'Queens:Astoria_Heights',\
 'Queens:Auburndale',\
 'Queens:Bay_Terrace',\
 'Queens:Bayside',\
 'Queens:Beechurst',\
 'Queens:Bellaire',\
 'Queens:Belle_Harbor',\
 'Queens:Bellerose',\
 'Queens:Breezy_Point',\
 'Queens:Briarwood',\
 'Queens:Cambria_Heights',\
 'Queens:College_Point',\
 'Queens:Corona',\
 'Queens:Douglaston',\
 'Queens:Downtown_Flushing',\
 'Queens:East_Elmhurst',\
 'Queens:Edgemere',\
 'Queens:Elmhurst',\
 'Queens:Far_Rockaway',\
 'Queens:Floral_Park',\
 'Queens:Flushing',\
 'Queens:Flushing_Meadows',\
 'Queens:Forest_Hills',\
 'Queens:Fresh_Meadows',\
 'Queens:Glen_Oaks',\
 'Queens:Glendale',\
 'Queens:Hillcrest',\
 'Queens:Hollis',\
 'Queens:Holliswood',\
 'Queens:Howard_Beach',\
 'Queens:Hunters_Point',\
 'Queens:JFK_Airport',\
 'Queens:Jackson_Heights',\
 'Queens:Jamaica',\
 'Queens:Jamaica_Estates',\
 'Queens:Jamaica_Hills',\
 'Queens:Kew_Gardens',\
 'Queens:Kew_Gardens_Hills',\
 'Queens:LaGuardia_Airport',\
 'Queens:Laurelton',\
 'Queens:Lindenwood',\
 'Queens:Little_Neck',\
 'Queens:Long_Island_City',\
 'Queens:Malba',\
 'Queens:Maspeth',\
 'Queens:Middle_Village',\
 'Queens:Murray_Hill',\
 'Queens:North_Corona',\
 'Queens:Oakland_Gardens',\
 'Queens:Ozone_Park',\
 'Queens:Pomonok',\
 'Queens:Queens_Village',\
 'Queens:Queensborough_Hill',\
 'Queens:Rego_Park',\
 'Queens:Richmond_Hill',\
 'Queens:Ridgewood',\
 'Queens:Rochdale',\
 'Queens:Rockaway_Park',\
 'Queens:Rosedale',\
 'Queens:Seaside',\
 'Queens:Somerville',\
 'Queens:Springfield_Gardens',\
 'Queens:Steinway',\
 'Queens:Sunnyside',\
 'Queens:Utopia',\
 'Queens:Whitestone',\
 'Queens:Woodhaven',\
 'Queens:Woodside',\
 'Bronx:Baychester',\
 'Bronx:Bedford_Park',\
 'Bronx:Belmont',\
 'Bronx:Castle_Hill',\
 'Bronx:City_Island',\
 'Bronx:Claremont_Village',\
 'Bronx:Clason_Point',\
 'Bronx:Co-op_City',\
 'Bronx:Concourse',\
 'Bronx:Concourse_Village',\
 'Bronx:Country_Club',\
 'Bronx:East_Tremont',\
 'Bronx:Eastchester',\
 'Bronx:Edenwald',\
 'Bronx:Edgewater_Park',\
 'Bronx:Fieldston',\
 'Bronx:Fordham',\
 'Bronx:High_Bridge',\
 'Bronx:Hunts_Point',\
 'Bronx:Kingsbridge',\
 'Bronx:Longwood',\
 'Bronx:Melrose',\
 'Bronx:Morris_Heights',\
 'Bronx:Morris_Park',\
 'Bronx:Morrisania',\
 'Bronx:Mott_Haven',\
 'Bronx:Mount_Eden',\
 'Bronx:Mount_Hope',\
 'Bronx:North_Riverdale',\
 'Bronx:Norwood',\
 'Bronx:Olinville',\
 'Bronx:Parkchester',\
 'Bronx:Pelham_Bay',\
 'Bronx:Pelham_Gardens',\
 'Bronx:Port_Morris',\
 'Bronx:Riverdale',\
 'Bronx:Schuylerville',\
 'Bronx:Soundview',\
 'Bronx:Spuyten_Duyvil',\
 'Bronx:Throgs_Neck',\
 'Bronx:Unionport',\
 'Bronx:University_Heights',\
 'Bronx:Van_Nest',\
 'Bronx:Wakefield',\
 'Bronx:West_Farms',\
 'Bronx:Westchester_Square',\
 'Bronx:Williamsbridge',\
 'Bronx:Woodlawn'] \
}

counts = { 'BOS':\
    [1778,  660, 325, 4509, 820, 418, 1049, 1048, 874, 661, 457, 2652, \
    4753, 221, 571, 1669, 1123, 120, 398, 105, 5597, 1408, 159, 1028, 222, \
    1188, 1083, 427, 828, 128, 151, 741, 1142, 476, 842, 182, 4518, 1979, \
    94, 117, 3133, 1043, 312, 521],\
    'NYC':\
    [2100, 4098, 5675, 5311, 322, 1172, 6063, 2372, 2922, 1645, 3910, 1678,\
    675, 257, 1543, 908, 208, 1080, 4330, 367, 1004, 350, 1698, 1830, 2430,\
    1527, 2926, 5905, 733, 1111, 1217, 728, 117, 1924, 3734, 2784, 624, 919, \
    165, 1893, 6327, 690, 155, 845, 96, 1179, 251, 3219, 1197, 1233, 36, 759, \
    651, 114, 3033, 1690, 2129, 89, 172, 4012, 426, 291, 2430, 1117, 430, 1611,\
    1811, 698, 189, 11260, 6144, 3232, 4107, 4889, 13569, 13829, 2669, 5074, \
    5764, 9574, 1148, 2629, 3861, 1387, 4314, 1852, 82, 1221, 42608, 52768, \
    655, 10227, 1326, 923, 180, 3692, 412, 2296, 889, 10138, 5424, 378, \
    2670, 17569, 8262, 4996, 4099, 6242, 99, 7342, 179, 1206, 358, 2346, \
    526, 96, 62, 266, 39, 569, 478, 1019, 705, 794, 4735, 179, 53, 3494, \
    835, 320, 11623, 119, 4092, 490, 281, 1343, 654, 441, 59, 218, 1214, \
    351, 2886, 5330, 94, 78, 768, 1169, 89, 747, 548, 198, 4301, 292, 1694, \
    1079, 1731, 1171, 566, 4093, 192, 1349, 311, 1773, 1670, 2055, 1550, 414, \
    274, 306, 117, 1277, 616, 3123, 418, 556, 563, 2312, 381, 866, 1072, 272, \
    215, 801, 174, 400, 1276, 602, 203, 1117, 479, 869, 256, 96, 1293,\
    300, 620, 670, 1083, 466, 659, 734, 1206, 2192, 594, 691, 398, 1187, 244, \
    757, 486, 1843, 271, 571, 701, 967, 255, 112, 689, 137, 311, 237, 715, \
    774, 615, 493] \
    }



city_prefix = {'BOS' : "p:MA:Boston::", 'NYC': "p:NY:New_York:"}

def get_yelp_neighborhood_string(s):
    html = readparse(s,'http://www.yelp.com/search?find_loc=Brooklyn%2C+NY')
    items = html.findAll('label', {'class': 'place radio-check'})
    itemlist = [item.find()['value'] for item in items]
    n = []
    print itemlist
    for a in itemlist:
        m = re.search(r'NY:New_York:(\w+:\w+)',a)
        if m:
            n.append(m.group(1))
    return n

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
    cats = {}
    for c in dirty_cats:
        tmp = c.contents[1::2]
        value = clean_dirty_cat(tmp)
        biz_name = parse_biz_names(c.find_parents(limit=2)[1])[0]
        cats[biz_name]= value
    return cats

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
        ratings[biz_name] = r.attrs['alt'][:3]
    return ratings



def yelp_by_neighborhood(city,neighborhood,max_search=1000,sleep=True):
    # scrapes yelp results page for business information in map script
    tst = "http://www.yelp.com/search?&l="+city_prefix[city]\
            + neighborhood + "&start=0"
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
        tst = "http://www.yelp.com/search?&l=" +city_prefix[city] \
                + neighborhood + "&start=" + str(start_page)
        html = readparse(s, tst)

        latlon_dict = parse_latlon(html)
        names = parse_biz_names(html)
        cats = parse_cats(html)
        dollars = parse_dollars(html)
        ratings = parse_ratings(html)

        temp_dict = clean_latlon_dict(latlon_dict)

        for n in cats.keys():
            temp_dict[n]['categories'] = cats[n]
        for n in ratings.keys():
            temp_dict[n]['stars']= ratings[n]

        for n in dollars.keys():
            temp_dict[n]['dollars'] = dollars[n]

        biz_dict.update(temp_dict)
        if sleep:
            time.sleep(random.uniform(1,4))
    return N, biz_dict

def record_neighborhood(city, nid,biz_dict):
    filename = 'neighborhoods/'+ city + '_' +  str(nid)+'.json'
    with open(filename,'w') as f:
        json.dump(biz_dict,f)

def parse_all_neighborhoods(city, neighborhoods,start_num,sleep= True):
    counts = []
    for neighborhood,nid in zip(neighborhoods[start_num:],range(start_num,len(neighborhoods))):
        print neighborhood
        N, biz_dict = yelp_by_neighborhood(city, neighborhood,sleep=sleep)
        record_neighborhood(city,nid, biz_dict)
        counts.append(N)
    print counts

def parse_num_bus_per_neighborhood(city):
    s = requests.Session()
    nids = []
    counts = []
    for nid,neighborhood in enumerate(neighborhoods[city]):
        if nid < 180:
            continue
        print nid
        tst = "http://www.yelp.com/search?&l=" +city_prefix[city] + \
                neighborhood+ "&start=0"
        html = readparse(s,tst)
        pgntn = html.find_all("span",{"class":"pagination-results-window"})[0].text
        m = re.search(r'of\s(.+)',pgntn)
        N = int(m.group(1))
        counts.append(N)
        nids.append(nid)
    return nids, counts
    #filename = 'neighborhoods/'+ city + '_' +  str(nid)+'.json'
    #with open(filename,'w') as f:
    #    json.dump(biz_dict,f)
