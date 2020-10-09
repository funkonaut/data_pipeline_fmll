###############################################################
#############       FIND THE LAND LORDS         ###############
###############################################################
#Residential props  ['100','113','150','160','210','220','230','240','330']
#df_tcad['res'] = (df_tcad.res | df_tcad.land_use.isin(res_code))
#df_tcad = df_tcad.loc[df_tcad.res]
df_tcad.address.fillna('MISSING ADDRESS',inplace=True) #change to 0 for fuzz match
df_tcad.owner_add.fillna('NO ADDRESS FOUND',inplace=True) #change to 0 for fuzz match

#Determine landlord criteria
df_tcad['single_unit'] = np.where(df_tcad.units_x>1, False, True)
#See if mailing address and address match up is 75 too HIGH???  
df_tcad['score'] = df_tcad.apply(lambda x: fuzz.partial_ratio(x.address,x.owner_add),axis=1)
df_tcad['add_match'] = np.where((df_tcad.score > 70), True, False)
#Multiple property owner
df_tcad['multi_own'] = df_tcad.duplicated(subset='py_owner_i')  #multiple owner ids
df_tcad['multi_own1'] = df_tcad.duplicated(subset='prop_owner') #multiple owner names
#df_tcad['multi_own2'] = df_tcad.duplicated(subset='mail_add_2') #multiple owner_add subsets
df_tcad['multi_own3'] = df_tcad.duplicated(subset='owner_add')  #multiple owner_add
#props with no address should be nan 
df_tcad.address.replace('MISSING ADDRESS',np.nan,inplace=True)
df_tcad.owner_add.replace('NO ADDRESS FOUND',np.nan,inplace=True) #change to 0 for fuzz match

#If single unit addresses match zips match not a biz and not a multi owner
#maybe include hs figure out how to use to get corner cases?
df_ll = df_tcad.loc[df_tcad.res & (~((df_tcad.single_unit)&(df_tcad.add_match)&(~(df_tcad.multi_own|df_tcad.multi_own1|df_tcad.multi_own3))))]

#Drop non residential locations and city properties that slipped through the algorithm
df_ll = df_ll.loc[~(df_ll.address=='VARIOUS LOCATIONS')] #No idea what these are but they dont belong
df_ll = df_ll.loc[~(df_ll.address=='*VARIOUS LOCATIONS')] #No idea what these are but they dont belong
df_ll = df_ll.loc[~(df_ll.owner_add.str.contains('PO BOX 1088 ',na=False))] #City of Austin
df_ll = df_ll.loc[~(df_ll.owner_add.str.contains('PO BOX 1748 ',na=False))] #Travis County
df_ll = df_ll.loc[df_ll.address.str.len()>=5] #get rid of properties with bad addresses as they all have none type prop_owner  (cant filter out weird bug?)
df_ll = df_ll.loc[~(df_ll.owner_add.str.contains('PO BOX 15426',na=False))] #State of Texas 
df_ll = df_ll.loc[~(df_ll.owner_add.str.contains('PO BOX 17126',na=False))] #Land Fills why are these coded res?
df_ll = df_ll.loc[df_ll.land_use!=640] #schools
com_type = ['OFF/RETAIL (SFR)',  'COMMERCIAL SPACE CONDOS', 'SM OFFICE CONDO', 'LG OFFICE CONDO', 'OFFICE (SMALL)','SM STORE <10K SF', 'STRIP CTR <10000', 'WAREHOUSE <20000', "MF'D COMMCL BLDG", 'OFFICE LG >35000', 'MEDICAL OFF <10K','PARKING GARAGE']
df_ll = df_ll.loc[~(df_ll.type1.isin(com_type)&(~df_ll.land_use.isin(res_code)))] #office condos that are not mixed use

#Handle more missing 
df_ll.X_x = df_ll.groupby(['st_name','st_number']).X_x.transform('ffill')
df_ll.X_x = df_ll.groupby(['st_name','st_number']).X_x.transform('bfill')
df_ll.Y_x = df_ll.groupby(['st_name','st_number']).Y_x.transform('ffill')
df_ll.Y_x = df_ll.groupby(['st_name','st_number']).Y_x.transform('bfill')

#Combine units with same prop owner and same address
#df_ll.units_x = df_ll.groupby(['address','prop_owner'])['units_x'].transform('sum')
#df_ll.drop_duplicates(['address','prop_owner'],inplace=True)

#Add in values from eviction data
#df_e = pd.read_csv('Evictions_filled_partial_9_26.csv')
#df_e['prop_id'] = df_e['Property ID']
#df_e = df_e.loc[df_e.prop_id.notnull()]
#df_eid = df_e[['prop_id','Lat','Long']]
#df_eid = df_eid.merge(df_tcad,on='prop_id',how='left')
#cols = df_tcad.columns.tolist()
#df_ll = df_eid.merge(df_ll,on=cols,how='outer').drop_duplicates('prop_id')

#df_ll.Y_x.fillna(df_ll.Lat,inplace=True)
#df_ll.X_x.fillna(df_ll.Long,inplace=True)
#df_e.loc[~df_e.prop_id.isin(df_ll.prop_id.values)]

#Fill in imputed values 
df_ll.units_x.fillna(df_ll['unit_est'],inplace=True)
#Round it and correct 
df_ll.units_x = round(df_ll.units_x)
df_ll.units_x = np.where(df_ll.units_x<1, 1, df_ll.units_x)
#Fill in with property unit estimations on ly where the low of the range estimate is higher then the imputated value
df_ll.units_x = np.where((df_ll.low>df_ll.units_x)&(df_ll.known==False),df_ll.low,df_ll.units_x)
#Get rid of estimates from type that are above 1k
df_ll.units_x = np.where((df_ll.units_x>1000),np.nan,df_ll.units_x)

#Export for dedupe and affiliation clustering
df_ll_dup = df_ll[['prop_owner','py_owner_i','address','owner_add','prop_id','DBA']]
df_ll_dup.to_csv('./land_lords.csv',index=False)

df_ll['land_lord_res'] = (((df_ll.units_x==1)&df_ll.add_match) | ((df_ll.hs=='T')&(df_ll.units_x==1)))

#df_ll.loc[(df_ll.hs=='T')&(df_ll.units_x>2)&(df_ll.known)][['prop_owner','owner_add','address','units_x','type1','low']]

#Export shape file and csv file for prelim check in qGIS
#coor_to_geometry(df_ll,col=['X_x_x','Y_x_x'],out='geometry')
#keep = ['prop_id', 'py_owner_i', 'prop_owner', 'DBA', 'address', 'owner_add','units_x','geometry'] 
#gdf_ll = geopandas.GeoDataFrame(df_ll,geometry='geometry')
#clean_up(gdf_ll,cols=keep,delete=False)
#gdf_ll.to_file("all_landlords.shp")

#pid= []
#cols = [ 'desc'      ,'DBA'       ,'address'   ,'owner_add' ,'type1']
#for col in cols:
#  pid.append(df_tcad.loc[df_tcad[col].str.contains('COMMERCIAL',na=False)].prop_id.tolist())
#
#pid = list(set(pid))
#
#df_tcad.loc[~df_tcad.prop_id.isin(pid)]
