####################################################################
#                    BUILD AFFILIATION LIST                        #
####################################################################
df_aff = pd.read_csv('../land_lord_locate/dedupe-examples/csv_example/trial7.csv')
df_aff = df_ll.merge(df_aff,on=['prop_id','py_owner_i','address','owner_add','prop_owner'])

#MAKE SURE TO CLEANUP ADDRESS TO LOOK GOOD IE STRIP WHITE SPACES
df_aff.address = df_aff.address.str.rstrip()
df_aff.address = df_aff.address.str.lstrip()
df_aff.address = df_aff.address.str.replace(' +',' ')
df_aff.owner_add = df_aff.owner_add.str.rstrip()
df_aff.owner_add = df_aff.owner_add.str.lstrip()
df_aff.owner_add = df_aff.owner_add.str.replace(' +',' ')

#Drop null owner addresses and null loctions
#4k props lost :( 
df_aff.dropna(subset=['X_x_x','Y_x_x'], inplace=True)
df_aff = df_aff.loc[~df_aff['owner_add'].isnull()]

#Get rid of misc info 
keep = ['known','Cluster ID','prop_id', 'py_owner_i', 'prop_owner', 'address', 'owner_add','units_x','X_x_x','Y_x_x','value']
df_aff = df_aff[keep]

#Calculate units and properties owned by deduped clusters
df_aff['Properties Held by Taxpayer Match Code'] = df_aff.groupby('Cluster ID')['prop_id'].transform('count')
df_aff['Estimated Total Unit Count'] = df_aff.groupby('Cluster ID')['units_x'].transform('sum')
df_aff['Total Appraisal Value of Properties'] = df_aff.groupby('Cluster ID')['value'].transform('sum')

#Rename to names in database (refer to constant.js)
df_aff.columns = ["known","Taxpayer Match Code","Property Index Number","Taxpayer Match Code (TCAD)","Taxpayer","Property Address",'Affiliated With','Unit Count from Department of Buildings','X','Y','Appraisal Value','Properties Held by Taxpayer Match Code','Estimated Total Unit Count','Total Appraisal Value of Properties']
df_aff['Additional Details']= '' 

#Clean up from upper case to Title
df_aff['Taxpayer']         = df_aff['Taxpayer'].apply(lambda x:  " ".join(w.capitalize() for w in x.split())) 
df_aff['Property Address'] = df_aff['Property Address'].apply(lambda x:  " ".join(w.capitalize() for w in x.split())) 
df_aff['Affiliated With']  = df_aff['Affiliated With'].apply(lambda x:  " ".join(w.capitalize() for w in x.split())) 

#Make sure types are right
df_aff["Properties Held by Taxpayer Match Code"] = df_aff["Properties Held by Taxpayer Match Code"].astype(int)
df_aff["Unit Count from Department of Buildings"] = df_aff["Unit Count from Department of Buildings"].astype(int)
df_aff["Taxpayer Match Code"] = df_aff["Taxpayer Match Code"].astype(str)
df_aff["Property Index Number"] = df_aff["Property Index Number"].astype(str)

#Build search index  
df_search = pd.DataFrame(df_aff, columns = ['Property Index Number','Property Address'])
df_search.to_json('search_index.json')

#Build map tiles
gdf_all = df_to_geojson(df_aff,["Property Index Number","Taxpayer Match Code","Taxpayer","Property Address",'Affiliated With','Unit Count from Department of Buildings','Properties Held by Taxpayer Match Code','Estimated Total Unit Count','Total Appraisal Value of Properties', 'Additional Details'],lat='Y',lon='X')
with open('props_all_9_20.geojson', 'w') as fp:
    json.dump(gdf_all,fp)

df_aff100 = df_aff.loc[df_aff['Estimated Total Unit Count']>=100]
gdf100 = df_to_geojson(df_aff100,["Property Index Number","Taxpayer Match Code","Taxpayer","Property Address",'Affiliated With','Unit Count from Department of Buildings','Properties Held by Taxpayer Match Code','Estimated Total Unit Count','Total Appraisal Value of Properties', 'Additional Details'],lat='Y',lon='X')
with open('props100_9_20.geojson', 'w') as fp:
    json.dump(gdf100,fp)

df_aff10 = df_aff.loc[(99>=df_aff['Estimated Total Unit Count'])&(df_aff['Estimated Total Unit Count']>=10)]
gdf10 = df_to_geojson(df_aff10,["Property Index Number","Taxpayer Match Code","Taxpayer","Property Address",'Affiliated With','Unit Count from Department of Buildings','Properties Held by Taxpayer Match Code','Estimated Total Unit Count','Total Appraisal Value of Properties', 'Additional Details'],lat='Y',lon='X')
with open('props10_9_20.geojson', 'w') as fp:
    json.dump(gdf10,fp)

df_aff3 = df_aff.loc[(9>=df_aff['Estimated Total Unit Count'])&(df_aff['Estimated Total Unit Count']>=3)]
gdf3 = df_to_geojson(df_aff3,["Property Index Number","Taxpayer Match Code","Taxpayer","Property Address",'Affiliated With','Unit Count from Department of Buildings','Properties Held by Taxpayer Match Code','Estimated Total Unit Count','Total Appraisal Value of Properties', 'Additional Details'],lat='Y',lon='X')
with open('props3_9_20.geojson', 'w') as fp:
    json.dump(gdf3,fp)

df_aff1 = df_aff.loc[(2>=df_aff['Estimated Total Unit Count'])&(df_aff['Estimated Total Unit Count']>=1)]
gdf1 = df_to_geojson(df_aff1,["Property Index Number","Taxpayer Match Code","Taxpayer","Property Address",'Affiliated With','Unit Count from Department of Buildings','Properties Held by Taxpayer Match Code','Estimated Total Unit Count','Total Appraisal Value of Properties', 'Additional Details'],lat='Y',lon='X')
with open('props1_9_20.geojson', 'w') as fp:
    json.dump(gdf1,fp)



