####################################################################
#                    BUILD AFFILIATION LIST                        #
####################################################################
#Possible affiliations
df_o_aff = pd.read_csv('../land_lord_locate/dedupe-examples/csv_example/trial10.csv')
#Probable affiliations
df_m_aff = pd.read_csv('../land_lord_locate/dedupe-examples/csv_example/trial9.csv')

#Some known regrouping: affordable housing projects
df_m_aff.loc[df_m_aff['owner_add'].str.contains('3000 S ',na=False),'Cluster ID'] = 7

#Put both data sets together Cluster_x owner add and name match Cluster_y name match
del df_o_aff['Cluster ID.1']
del df_o_aff['confidence_score.1']
df_aff = df_m_aff.merge(df_o_aff, on = ['prop_owner','py_owner_i','address','owner_add','prop_id'])
df_aff = df_ll.merge(df_aff,on=['prop_id','py_owner_i','address','owner_add','prop_owner'])

#Get rid of known false positive 
df_aff = df_aff.loc[~df_aff.prop_owner.str.contains('Owners Club',na=True)]
#personal property why is this code leading to 50 props missing? 
idxs = df_ll.loc[df_ll.type=='P'].prop_id.tolist()
df_aff = df_aff.drop(df_aff.loc[df_aff['prop_id'].isin(idxs)].index)

#Clean up addresses and displayed information
df_aff.address    = clean_string(df_aff,'address')
df_aff.owner_add  = clean_string(df_aff,'owner_add')
df_aff.prop_owner = clean_string(df_aff,'prop_owner')

#Drop null owner addresses and null loctions 3k props lost 
df_aff.dropna(subset=['X_x','Y_x'], inplace=True)

#Replace nulls
df_aff.units_x.fillna(1,inplace=True) #unknown units atleast 1 

#Get rid of misc info 
keep = ['hs','land_lord_res','est_from_type','known','Cluster ID_x','Cluster ID_y','prop_id', 'py_owner_i', 'prop_owner', 'address', 'owner_add','units_x','X_x','Y_x','value']
df_aff = df_aff[keep]

#Calculate units and properties owned by deduped clusters
df_aff['Estimated Total Unit Count'] = df_aff.groupby('Cluster ID_y')['units_x'].transform('sum')
df_aff['Total Appraisal Value of Properties'] = df_aff.groupby('Cluster ID_y')['value'].transform('sum')
df_aff['Possible Affiliates ID'] = df_aff['Cluster ID_x']

#Make sure types are right
df_aff['Estimated Total Unit Count'] = df_aff['Estimated Total Unit Count'].astype(int)
df_aff['units_x'] = df_aff['units_x'].astype(int)
df_aff['Cluster ID_y'] = df_aff['Cluster ID_y'].astype(str)
df_aff["prop_id"] = df_aff["prop_id"].astype(int).astype(str)
df_aff['Cluster ID_x'] = df_aff['Cluster ID_x'].astype(str)

#Group owners at same address sum their units so we can drop them to make for cleaner plotting
df_aff['units_x'] = df_aff.groupby(['prop_owner','address']).units_x.transform('sum')
df_aff.drop_duplicates(['prop_owner','address'],inplace=True)

#Jitter overlapping points
df_spread = df_aff.loc[df_aff.duplicated(['X_x','Y_x'])]
df_spread.Y_x = df_spread.Y_x.astype(float)
df_spread.X_x = df_spread.X_x.astype(float)
sigma = .0001 #changed from .0001
df_spread.X_x = df_spread.X_x.apply(lambda x: np.random.normal(x, sigma))
df_spread.Y_x = df_spread.Y_x.apply(lambda x: np.random.normal(x, sigma))
clean_up(df_spread,['prop_id','X_x','Y_x'])
df_aff = df_aff.merge(df_spread,on='prop_id',how='left')
df_aff.X_x_x = np.where(df_aff.X_x_y.notnull(),df_aff.X_x_y,df_aff.X_x_x)
df_aff.Y_x_x = np.where(df_aff.Y_x_y.notnull(),df_aff.Y_x_y,df_aff.Y_x_x)

#Drop ll residences 
df_aff.drop(df_aff.loc[df_aff.land_lord_res==True].index,inplace=True)

#Take away one from unit count where HS is true
df_aff.units_x = np.where(df_aff.hs=='T', df_aff.units_x-1, df_aff.units_x)

#Replace estimates with 0 for displaying 
df_aff.units_x = np.where((df_aff.known|df_aff.est_from_type),df_aff.units_x, 0)

#Clean up
#del df_aff['known']
del df_aff['Cluster ID_x']
del df_aff['py_owner_i']
del df_aff['est_from_type']
del df_aff['X_x_y']
del df_aff['Y_x_y']
del df_aff['land_lord_res']
del df_aff['hs']

#Rename to names in database (refer to constant.js)
df_aff.columns = ['Taxpayer Match Code','Property Index Number', "Taxpayer","Property Address",'Affiliated With','Unit Count from Department of Buildings','X','Y','Appraisal Value','Properties Held by Taxpayer Match Code','Total Appraisal Value of Properties','Possible Affiliates ID']
df_aff['Additional Details']= '' 

###Testing: Export shape file and csv file for prelim check in qGIS
##coor_to_geometry(df_aff,col=['X','Y'],out='geometry')
##gdf_ll = geopandas.GeoDataFrame(df_aff,geometry='geometry')
##gdf_ll.to_file("all_landlords.shp")
##del df_aff['geometry']


#Build search index  
fs = '_10_1.json' 
df_search = pd.DataFrame(df_aff, columns = ['Property Index Number','Property Address'])
df_search.to_json('search_index'+fs,orient = 'records')

##Build map tiles
#gdf_all = df_to_geojson(df_aff,["Taxpayer Match Code","Property Index Number", "Taxpayer","Property Address",'Affiliated With','Unit Count from Department of Buildings','Appraisal Value','Properties Held by Taxpayer Match Code','Total Appraisal Value of Properties','Possible Affiliates ID','Additional Details'],lat='Y',lon='X')
#with open('props_all'+fs, 'w') as fp:
#    json.dump(gdf_all,fp)
#
#df_aff100 = df_aff.loc[df_aff['Properties Held by Taxpayer Match Code']>=100]
#gdf100 = df_to_geojson(df_aff100,["Taxpayer Match Code","Property Index Number", "Taxpayer","Property Address",'Affiliated With','Unit Count from Department of Buildings','Appraisal Value','Properties Held by Taxpayer Match Code','Total Appraisal Value of Properties','Possible Affiliates ID','Additional Details'],lat='Y',lon='X')
#with open('props100'+fs, 'w') as fp:
#    json.dump(gdf100,fp)
#
#df_aff10 = df_aff.loc[(99>=df_aff['Properties Held by Taxpayer Match Code'])&(df_aff['Properties Held by Taxpayer Match Code']>=10)]
#gdf10 = df_to_geojson(df_aff10,["Taxpayer Match Code","Property Index Number", "Taxpayer","Property Address",'Affiliated With','Unit Count from Department of Buildings','Appraisal Value','Properties Held by Taxpayer Match Code','Total Appraisal Value of Properties','Possible Affiliates ID','Additional Details'],lat='Y',lon='X')
#with open('props10'+fs, 'w') as fp:
#    json.dump(gdf10,fp)
#
#df_aff3 = df_aff.loc[(9>=df_aff['Properties Held by Taxpayer Match Code'])&(df_aff['Properties Held by Taxpayer Match Code']>=3)]
#gdf3 = df_to_geojson(df_aff3,["Taxpayer Match Code","Property Index Number", "Taxpayer","Property Address",'Affiliated With','Unit Count from Department of Buildings','Appraisal Value','Properties Held by Taxpayer Match Code','Total Appraisal Value of Properties','Possible Affiliates ID','Additional Details'],lat='Y',lon='X')
#with open('props3'+fs, 'w') as fp:
#    json.dump(gdf3,fp)
#
#df_aff1 = df_aff.loc[(2>=df_aff['Properties Held by Taxpayer Match Code'])&(df_aff['Properties Held by Taxpayer Match Code']>=1)]
#gdf1 = df_to_geojson(df_aff1,["Taxpayer Match Code","Property Index Number", "Taxpayer","Property Address",'Affiliated With','Unit Count from Department of Buildings','Appraisal Value','Properties Held by Taxpayer Match Code','Total Appraisal Value of Properties','Possible Affiliates ID','Additional Details'],lat='Y',lon='X')
#with open('props1'+fs, 'w') as fp:
#    json.dump(gdf1,fp)
#
#
