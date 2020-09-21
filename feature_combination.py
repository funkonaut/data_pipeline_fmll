########################
### Feature combine  ###
########################
#Combine code and tcad takes around 10min for fuzzy matching lose around 11k code complaints :( try to add back in using polygon from gdf and location points
#get rid of nan in address long st number and st name
#df_code.dropna(subset=['ADDRESS_LONG','HOUSE_NUMBER','STREET_NAME'],inplace=True)
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

