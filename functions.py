#####################
###   CODE INFO   ###
######################
#This code compiles all the city data sets
#into one that has the following properties
# "Property Address"
# "Community Area"
# "Property Index Number"
# "Taxpayer"
# "Taxpayer Match Code"
# "Affiliated With"
# "Additional Details"
# "Properties Held by Taxpayer Match Code"
# "Unit Count from Department of Buildings"
# "Relative Size"

#######################
###    DATA SETS    ###
#######################
#df_tcad:   all appraisal data not geo located no unit numbers unique: prop_id, py_owner_i 
#df_units:  unit estimates based on improvement data (only includes properties that have been improved) unique: prop_id
#gdf:       location of all building and land coding from land use code (does not locate properties just parcels) uniqe:property_i (prop_id)
#gdf_16     complete data set from 2016 used to fill in missing unit info owner info of old properties unique(prop_id) 
#df_locs:   location data from city unique: PROP_ID
#df_code:   code violations unique: LATITUDE,LONGITUDE
#df_fill:   census scraped locations
import json
import pandas as pd
import geopandas
import numpy as np
from shapely import wkt
from fuzzywuzzy import fuzz
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

def clean_up(df,cols=[] ,delete=False):
    if delete:
        for col in cols:
            del df[col]
    else:
        for col in df.columns:
            if col not in cols:
                del df[col]

###TEST THAT UNKNOWN IS NAN ******
#extract year from float date (col) and create new column if property is newer then 2016
def extract_new_props(df,col):
    df[col]= df[col].astype(str).str[-4:-2]
    df[col].replace('n',21,inplace=True)    #assume nulls are new unit proven otherwise
    df[col] = df.loc[df[col].notnull()][col].astype(int)
    df['new'] = np.where((df[col]<21)&(df[col]>16) , True, False)
    df['new'] = np.where((df[col]==21) , np.nan, df.new)

def extract_nums(df,col):
    a = df[col].str.extractall('(\d+)').astype(float)
    df = df.join(a[0].unstack()).fillna('')
    return df

def extract_num(df,col):
    return df[col].str.extract('(\d+)').astype(float)

def replace_nan(df,cols=[],val=0,reverse=False):
    if not reverse:
        for col in cols:
            df[col].replace(np.nan,val,inplace=True)
    else:
        for col in cols:
            df[col].replace(val,np.nan,inplace=True)

def convert_to_numeric(df, col):
    #extract first group of number in string maybe improve so it caputres all numbers
    num = extract_num(df,col)
    replace_nan(num,num.columns)
    try:
       return num.astype(int)
    except ValueError:
       print(ValueError)

#concatenates string columns with empty values           
def combine_string_cols(df,cols=[],out='out'):
    replace_nan(df,cols,val='',reverse=False)
    address = ''
    for col in cols:
        address += df[col].astype(str) + ' '
    df[out]=address#.apply(lambda x: pyap.parse(x, country='US'))

#extract coordinates from geopandas frame
def extract_coor(gdf,col='geometry',out=['X','Y']):
    try:
        gdf[out[0]]=gdf[col].centroid.x
        gdf[out[1]]=gdf[col].centroid.y
    except:
        gdf[out[0]]=gdf[col].x
        gdf[out[1]]=gdf[col].y

def coor_to_geometry(df,col=['X','Y'],out='geometry'):
    df[out]=geopandas.points_from_xy(df[col[0]],df[col[1]])

#merge on value (df2 + df3) + df1 (origin)
def merge_extraction(dfs=[],on='prop_id',val=['units']):
    df2_cp = dfs[1].copy()  #copy datasets so no info is lost
    df3_cp = dfs[2].copy()
    clean_up(df2_cp,[on]+val)  #cleanup all values out of datasets to extract info from
    clean_up(df3_cp,[on]+val)  #cleanup all values out of datasets to extract info from
    df3_cp = df3_cp.merge(df2_cp,on=on,how='outer')
    return dfs[0].merge(df3_cp,on=on,how='left') #keep all values from original data frame don't care about values not in org

def fill_in_locs(df):
    df2 = pd.DataFrame(columns=df.columns)
    df_add = df.groupby('address')
    for add,df in df_add:
        if df.X_x.notnull().any() and len(df.index)>1:
            df.sort_values(by='X_x',inplace=True)
            df.fillna(method='ffill',inplace=True)
            df2 = df2.append(df)
    return df2

def find_missing(df,col):
    return df.loc[df[col].isnull()]

def df_to_geojson(df, properties, lat='latitude', lon='longitude'):
    geojson = {'type':'FeatureCollection', 'features':[]}
    for _, row in df.iterrows():
        feature = {'type':'Feature',
                   'properties':{},
                   'geometry':{'type':'Point',
                               'coordinates':[]}}
        feature['geometry']['coordinates'] = [float(row[lon]),float(row[lat])]
        for prop in properties:
            if row[prop] != np.nan:
                feature['properties'][prop] = row[prop]
            else:
                feature['properties'][prop] = 'Info Not Availble'
        geojson['features'].append(feature)
    return geojson

