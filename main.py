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
from impyute.imputation.cs import mice
from scipy.spatial import cKDTree
from shapely.geometry import Point
import string
import re
import time
import operator

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from scipy.sparse import csr_matrix

import sparse_dot_topn.sparse_dot_topn as ct
pd.set_option('display.max_rows', 500)
print('Executing functions')
exec(open('functions.py').read())
print('Executing read_data')
exec(open('read_data.py').read())
print('Executing data_preprocess')
exec(open('data_preprocess.py').read())
print('Executing feature_extraction')
exec(open('feature_extraction.py').read())
print('Executing feature_combination')
exec(open('feature_combination.py').read())
print('Executing handle_missing')
exec(open('handle_missing.py').read())
print('Executing landlord_find')
exec(open('landlord_find.py').read())
#print('Run dedupe to build landlord affiliations')
#Run once for probable affiliations (name or taxpayer id the same) will need to change dedupe.py to output file name that matches the file read in in affiliate_code.py 
#exec(open('dedupe.py').read()) must run this in dedupe source code directory
#And again for possible affiliations (mail address the same) will need to change dedupe.py to output file name that matches the file read in in affiliate_code.py 
#exec(open('dedupe.py').read()) must run this in dedupe source code directory
#make sure above two are completed once this is ran
#print("Run code to clean up and format data and build estimates based on affiliation")
#exec(open('affiliate_code.py').read())



