###############################################################
#############       FIND THE LAND LORDS         ###############
###############################################################
#Residential props
res_type = ['DORMITORY HIRISE', 'DORMITORY','APARTMENT   5-25','LUXURY HI-RISE APTS 100+', 'APARTMENT 100+']
df_tcad['res'] = (df_tcad.res | df_tcad.type1.isin(res_type))
df_res = df_tcad.loc[df_tcad.res]
df_res.address.fillna('MISSING ADDRESS',inplace=True) #change to 0 for fuzz match
df_res.owner_add.fillna('NO ADDRESS FOUND',inplace=True) #change to 0 for fuzz match

#Determine landlord criteria
#Def a land lord if zips don't match
#df_res['zip_match'] = np.where(df_res.zip == df_res.mail_zip, True, False)
#Pos a landlord if more then 1 units?
df_res['single_unit'] = np.where(df_res.units_x>1, False, True)
#Def a landlord if DBA
#df_res['biz'] = np.where(df_res.DBA.notnull(), True, False)
#See if mailing address and address match up
#is 75 too HIGH??? Land 
df_res['score'] = df_res.apply(lambda x: fuzz.partial_ratio(x.address,x.owner_add),axis=1)
df_res['add_match'] = np.where((df_res.score > 70), True, False)
#Multiple property owner
df_res['multi_own'] = df_res.duplicated(subset='py_owner_i') 
df_res['multi_own1'] = df_res.duplicated(subset='prop_owner')
df_res['multi_own2'] = df_res.duplicated(subset='mail_add_2')
df_res['multi_own3'] = df_res.duplicated(subset='owner_add')
#props with no address should be nan 
df_res.address.replace('MISSING ADDRESS',np.nan,inplace=True)
df_res.owner_add.replace('NO ADDRESS FOUND',np.nan,inplace=True) #change to 0 for fuzz match
#If single unit addresses match zips match not a biz and not a multi owner
df_ll = df_res.loc[~((df_res.single_unit)&(df_res.add_match)&(~(df_res.multi_own|df_res.multi_own1|df_res.multi_own2|df_res.multi_own3)))]

#Drop land lord houses? or keep em in for unit estimation and then drop em?
df_ll['land_lord_res'] = (df_ll.hs=='T')&(df_ll.add_match)&df_ll.single_unit
#Drop non residential locations and city properties
df_ll = df_ll.loc[~(df_ll.address=='VARIOUS LOCATIONS')] #No idea what these are but they dont belong
df_ll = df_ll.loc[~(df_ll.address=='*VARIOUS LOCATIONS')] #No idea what these are but they dont belong
df_ll = df_ll.loc[~(df_ll.owner_add.str.contains('PO BOX 1088 ',na=False))] #City of Austin
df_ll = df_ll.loc[~(df_ll.owner_add.str.contains('PO BOX 1748 ',na=False))] #Travis County
df_ll = df_ll.loc[df_ll.address.str.len()>=5] #get rid of properties with bad addresses as they all have none type prop_owner  (cant filter out weird bug?)
df_ll = df_ll.loc[~(df_ll.owner_add.str.contains('PO BOX 15426',na=False))] #State of Texas 
df_ll = df_ll.loc[~(df_ll.code3.notnull())] #If code 3 is not null then its not res
df_ll = df_ll.loc[~(df_ll.owner_add.str.contains('PO BOX 17126',na=False))] #Land Fills why are these coded res?

#Combine units with same prop owner and same address
df_ll.units_x = df_ll.groupby(['address','prop_owner'])['units_x'].transform('sum')
df_ll.drop_duplicates(['address','prop_owner'],inplace=True)

#maybe forward fill properties with missing addresses 
#df_ll.sort_values(['st_name','st_number'],inplace=True)
#df_ll[['X_x','Y_x']]=df_ll[['X_x','Y_x']].fillna('ffill')

#Jitter overlapping points
df_spread = df_ll.loc[df_ll.duplicated(['X_x','Y_x'])]
df_spread.Y_x = df_spread.Y_x.astype(float)
df_spread.X_x = df_spread.X_x.astype(float)
sigma = .0001
#df_spread.Y_x = df_spread.Y_x.apply(lambda x: np.random.normal(x, sigma))
df_spread.X_x = df_spread.X_x.apply(lambda x: np.random.normal(x, sigma))
clean_up(df_spread,['prop_id','X_x','Y_x'])
df_ll=df_ll.merge(df_spread,on='prop_id',how='left')
df_ll.X_x_x = np.where(df_ll.X_x_y.notnull(),df_ll.X_x_y,df_ll.X_x_x)
#df_ll.Y_x_x = np.where(df_ll.Y_x_y.notnull(),df_ll.Y_x_y,df_ll.Y_x_x)

#keep = ['known','prop_id', 'py_owner_i', 'prop_owner', 'address', 'owner_add','units_x','X_x_x','Y_x_x','owner_add','value','land_lord_res','geometry_y','low','high'] 
#df_ll2 = df_ll[keep]
#Export for dedupe and affiliation clustering
df_ll_dup = df_ll[['prop_owner','py_owner_i','address','owner_add','prop_id']]
df_ll_dup.to_csv('./land_lords.csv',index=False)


#Export shape file and csv file
coor_to_geometry(df_ll2,col=['X_x_x','Y_x_x'],out='geometry')
keep = ['prop_id', 'py_owner_i', 'prop_owner', 'DBA', 'address', 'owner_add','units_x','geometry'] 
gdf_ll = geopandas.GeoDataFrame(df_ll2,geometry='geometry')
clean_up(gdf_ll,cols=keep,delete=False)
gdf_ll.to_file("all_landlords.shp")
