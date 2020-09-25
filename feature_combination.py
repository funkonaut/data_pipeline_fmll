########################
### Feature combine  ###
########################
#Combine Units:
df_tcad = merge_extraction(dfs=[df_tcad,df_units,gdf_16],val=['type1','units','low','high'])
replace_nan(df_tcad,['units_x','units_y','low','high'],val=0,reverse=True)
#Fill in with known data from improvements
df_tcad.units_x.fillna(df_tcad.units_y,inplace=True)
#Known units column
df_tcad['known']= np.where(df_tcad.units_x.notnull(), True,False)
#Fill in missing 2016 data with estimates and fill in outdated 2016 estimates with larger numbers
df_tcad.units_x = np.where(df_tcad.units_x < df_tcad.units_y, df_tcad.units_y, df_tcad.units_x)
del df_tcad['units_y']

#Combine Locations:
df_tcad = merge_extraction(dfs=[df_tcad,gdf,df_locs],on='prop_id',val=['land_use','X','Y','geometry'])
df_tcad.X_y.fillna(df_tcad.X_x,inplace=True)
df_tcad.Y_y.fillna(df_tcad.Y_x,inplace=True)
df_tcad.Y_x.fillna(df_tcad.Y_y,inplace=True)
df_tcad.X_x.fillna(df_tcad.X_y,inplace=True)
del df_tcad['X_y']
del df_tcad['Y_y']

df_tcad = df_tcad.merge(df_con,left_on='geo_id',right_on='TCAD ID',how='left')
df_tcad.Y_x.fillna(df_tcad.Latitude,inplace=True)
df_tcad.X_x.fillna(df_tcad.Longitude,inplace=True)
del df_tcad['Latitude']
del df_tcad['Longitude']

#Update res with new improvement type data include vacant tracks c1  905 Bedford St 78702?
res = ['A1','A2','A3','A4','A5','B1','B2','B3','B4','C1','M1','XA']
res_type = ['Detail Only'|'DORMITORY HIRISE', 'DORMITORY','APARTMENT   5-25','LUXURY HI-RISE APTS 100+', 'APARTMENT 100+']
df_tcad['res'] = df_tcad.code.isin(res)|df_tcad.code2.isin(res)|df_tcad.code3.isin(res)
df_tcad['res'] = (df_tcad.res | df_tcad.type1.isin(res_type) | (df_tcad.type1.str.contains('CONDO',na=False)))

#Combine eviction looks like I am missing some res units in the landlord map
#Only look at data with prop_ids
df_evict_m = df_evict.loc[df_evict['Property ID'].isnull()]

#clean up addresses
df1 = df_tcad
df1.address = df1.address.apply(lambda x:  " ".join(w.capitalize() for w in str(x).split()))
df1.owner_add = df1.owner_add.apply(lambda x:  " ".join(w.capitalize() for w in str(x).split()))
df1['st_name_full'] = df1.prefix + ' ' + df1.st_name + ' ' + df1.suffix
df1.st_name_full = df1.st_name_full.apply(lambda x:  " ".join(w.capitalize() for w in str(x).split()))

df_evict_m['Zip'] = df_evict_m['Zip'].astype(int).astype(str)
df_evict_m['Full Address'] = df_evict_m['Street Num'] + ' ' + df_evict_m['Street'] + ' ' + df_evict_m['Zip'] 

#see if owner occupied
df1['score'] = df1.apply(lambda x: fuzz.partial_ratio(x.address,x.owner_add),axis=1)
df1['add_match'] = np.where((df1.score > 70), True, False)
#Merge on address to get matches where properties are the exact
#df2 = df_evict_m.merge(df1,left_on=['Street'],right_on=['st_name_full'],how='left')
df3 = df_evict_m.merge(df1,left_on=['Street Num'],right_on=['st_number'],how='left')

#df2['match'] = df2.apply(lambda x: fuzz.partial_ratio(str(x['st_number']),str(x['Street Num'])),axis=1)
df3['match'] = df3.apply(lambda x: fuzz.partial_ratio(str(x['st_name_full']),str(x['Street'])),axis=1)

#df2_res = df2.loc[df2.res==True]
df3_res = df3#df3.loc[df3.res==True]
#df2_res.sort_values(['Case_Num','match'],ascending=False,inplace=True)
df3_res.sort_values(['Case_Num','match'],ascending=False,inplace=True)
#can this number be lower look at csv
#df2_res_m = df2_res.loc[df2_res.match>99]
df3_res_m = df3_res.loc[(df3_res.match>99)]

df3_res_m.prop_owner = df3_res_m.prop_owner.apply(lambda x:  " ".join(w.capitalize() for w in str(x).split())) 
df3_res_m.Plaintiff  = df3_res_m.Plaintiff.apply(lambda x:  " ".join(w.capitalize() for w in str(x).split())) 
df3_res_m['score_op'] = df3_res_m.apply(lambda x: fuzz.partial_ratio(x.Plaintiff,x.prop_owner),axis=1)

#Full partial address matches that only have one address are assumed correct
df_known = df3_res_m.loc[df3_res_m.groupby('Case_Num')['Case_Num'].transform('count') == 1]
df_unknown = df3_res_m.loc[df3_res_m.groupby('Case_Num')['Case_Num'].transform('count') != 1]
#Full partial owner plaintiff matches with properties with mult address matches are assumed correct
df_unknown = df_unknown.loc[df_unknown.score_op>99].drop_duplicates('prop_id')
df_unknown.sort_values('units_x',ascending=False,inplace=True)
df_known = df_known.append(df_unknown.drop_duplicates('Case_Num'))

df_known_id = df_known[care].merge(df_evict_m,on='Case_Num',how='right')
df_u = df_known_id.loc[df_known_id.prop_id.isnull()] 
del df_u['prop_id']

#look for nearest points of unknown in subset known much not matched and then in tcad data  
import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from shapely.geometry import Point

coor_to_geometry(df_u,['Long_y','Lat_y'])
gpd1 = gpd.GeoDataFrame(df_u)
df2 = df_tcad.loc[df_tcad.known_loc]
coor_to_geometry(df2,['X_x','Y_x'])
gpd2 = gpd.GeoDataFrame(df2)[['st_name_full','st_number','prop_owner','owner_add','prop_id','geometry']]

def ckdnearest(gdA, gdB):
    gdA = gdA.reset_index(drop=True)
    gdB = gdB.reset_index(drop=True)
    nA = np.array(list(gdA.geometry.apply(lambda x: (x.x, x.y))))
    nB = np.array(list(gdB.geometry.apply(lambda x: (x.x, x.y))))
    btree = cKDTree(nB)
    dist, idx = btree.query(nA, k=1)
    gdf = pd.concat(
        [gdA.reset_index(drop=True), gdB.loc[idx, gdB.columns != 'geometry'].reset_index(drop=True),
         pd.Series(dist, name='dist')], axis=1)
    return gdf

care = ['prop_owner', 'address', 'DBA', 'prop_id', 'known_loc','geometry','Case_Num', 'units_x', 'owner_add','match','score_op','dist']
gdf_res = ckdnearest(gpd1, gpd2)
gdf_res['match'] = gdf_res.apply(lambda x: fuzz.partial_ratio(str(x['st_name_full']),str(x['Street_y'])),axis=1)
gdf_res['match2'] = gdf_res.apply(lambda x: fuzz.partial_ratio(str(x['st_number']),str(x['Street Num_y'])),axis=1)
gdf_res['score_op'] = gdf_res.apply(lambda x: fuzz.partial_ratio(str(x['Plaintiff_y']),str(x['prop_owner'])),axis=1)
gdf_res['score_op2'] = gdf_res.apply(lambda x: fuzz.partial_ratio(str(x['Plaintiff_y']),str(x['owner_add'])),axis=1)
#Distance is very close or the street name and numbers match or the prop owner/owner_add and plaintiff match 
gdf_known = gdf_res.loc[(gdf_res.dist<0.00001)|((gdf_res.match>99)&(gdf_res.match2>99))|(gdf_res.score_op>99)|(gdf_res.score_op2>99)]

keep = ['Case_Num','prop_id']
df_k = df_known[keep].append(gdf_known[keep])
df_evict1 = df_evict.merge(df_k,on='Case_Num',how='left')
df_evict1['Property ID'].fillna(df_evict1.prop_id,inplace=True)
del df_evict1['prop_id']

#Why are ~100 case nums getting duplicated 
df_evict2 = df_evict1.merge(df_tcad,right_on='prop_id',left_on='Property ID',how='left').drop_duplicates('Case_Num')
df_evict2.Lat.fillna(df_evict2.X_x,inplace=True)
df_evict2.Long.fillna(df_evict2.Y_x,inplace=True)
df_evictf1 = df_evict2[['Lat', 'Long', 'Street Num', 'Street', 'City', 'Zip', 'Full address', 'Property ID', 'Active_Inactive', 'Date Filed', 'Case_Num', 'Plaintiff','units_x','prop_owner','owner_add','DBA','address']]
df_evictf1.to_csv('Evictions_filled_partial_9_24.csv')
#,columns=['Lat', 'Long', 'Street Num', 'Street', 'City', 'Zip', 'Full address', 'Property ID', 'Active_Inactive', 'Date Filed', 'Case_Num', 'Plaintiff','Unit Count (2016)','TCAD Property Owner','TCAD Owner Mailing Address','DBA','TCAD Address'])

#Cleanup any new data that was introduced that is not needed
del df_tcad['geometry']
del df_u['geometry']
#check 
care = ['add_match','address','owner_add','DBA','prop_id','known_loc','X_x','Y_x','Long','Lat','Case_Num','units_x']
df3_res_m.head(500)[care]
len(df3_res_md.Case_Num.unique())
#df1 = df_evict.merge(df_tcad,left_on=['Street Num','Zip'],right_on=['st_number','zip'],how='left')
df1.Street = df1.Street.str.upper()
df1['match'] = df1.apply(lamgbda x: fuzz.partial_ratio(str(x.st_name_full),str(x.Street)),axis=1)
#sort by res too?
df1.sort_values(['Case_Num','match'],ascending=False).drop_duplicates(['Case_Num'])[['res','match','Full address','address','owner_add','DBA','prop_id','known_loc','X_x','Y_x','Long','Lat','Case_Num','units_x']].to_csv('eviction_linked.csv',columns=['match','Full address','address','owner_add','DBA','prop_id','known_loc','X_x','Y_x','Long','Lat','Case_Num','units_x'])
#losing a lot with duplicate drop around 1k gone even without just missed from fuzzy match :(
#df1.loc[df1.match>99][['Full address','address','owner_add','DBA','prop_id','X_x','Y_x','Long','Lat','Case_Num','units_x']].drop_duplicates('prop_id')

#df_tcad.X_x = round(df_tcad.X_x.astype(float),4)
#df_tcad.Y_x = round(df_tcad.Y_x.astype(float),4)
#df_evict.Long = round(df_evict.Long,4)
#df_evict.Lat = round(df_evict.Lat,4)
#df1 = df_evict.merge(df_tcad,left_on=['Long','Lat'],right_on=['X_x','Y_x'])

#df_code_m = df_code.merge(df_tcad,right_on=['st_number'],left_on=['HOUSE_NUMBER'])
#df_code_m['match'] = df_code_m.apply(lambda x: fuzz.partial_ratio(x.st_name,x.STREET_NAME),axis=1)
#df_code_m2 = df_code_m.loc[df_code_m.match>99].drop_duplicates('CASE_ID')
##Try to handle missing
#df_miss = df_code.loc[~df_code.CASE_ID.isin(df_code_m2.CASE_ID)]
#df_miss_m=df_miss.merge(df_tcad,right_on=['st_number'],left_on=['HOUSE_NUMBER'])
##fuzzy match on address
#df_miss_m['match'] = df_miss_m.apply(lambda x: fuzz.partial_ratio(x.address,x.ADDRESS_LONG_x),axis=1)
#df_miss_m2 = df_miss_m.loc[(df_miss_m.groupby('ADDRESS_LONG_x')['match'].transform('max')==df_miss_m.match) & (df_miss_m.owner_add.notnull())]
#df_miss_m3 = df_miss_m2.loc[df_miss_m2.match>95] #this has false positives?
#df_code_linked = pd.concat([df_miss_m3,df_code_m2])
#df_code_linked['number_code'] = df_code_linked.groupby('prop_id').transform('count')['CASE_ID'] #only keep number of complaints for database
#df_code_linked.drop_duplicates('prop_id',inplace=True)
#clean_up(df_code_linked,['prop_id','number_code'])
#df_tcad = df_tcad.merge(df_code_linked,on='prop_id',how='left')

