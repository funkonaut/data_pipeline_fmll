########################
###  HANDLE MISSING  ###
########################
#Fill out known values for location
df_tcad['known_loc'] = np.where(df_tcad.X_x.notnull(),True,False)
#Fill in missing geometry is this working correctly? Various locations and somethings getting filled that are not really the same?
df_tcad.geometry_y = df_tcad.groupby('address').geometry_y.transform('ffill')
df_tcad.geometry_y = df_tcad.groupby('address').geometry_y.transform('bfill')
df_tcad.geometry_y = df_tcad.groupby(['st_name','st_number']).geometry_y.transform('ffill')
df_tcad.geometry_y = df_tcad.groupby(['st_name','st_number']).geometry_y.transform('bfill')
df_tcad.land_use = df_tcad.groupby('address').land_use.transform('ffill')
df_tcad.land_use = df_tcad.groupby('address').land_use.transform('bfill')
df_tcad.land_use = df_tcad.groupby(['st_name','st_number']).land_use.transform('ffill')
df_tcad.land_use = df_tcad.groupby(['st_name','st_number']).land_use.transform('bfill')

#Handle missing locations 
#Fill in based on geocoding census 
#df_miss = find_missing(df_tcad,'X_x')
#df_miss['state']='TX'
#df_miss.to_csv('./bulk_all.csv',columns=['address','city','state','zip'])
#exec(open('geocode.py').read()) #MAKE SURE LOWER LINE I IN GEOCODE DIR MAKE SURE GEOCODE DIR IS EMPTY BEFORE DOING THIS!!!!
df_fill = pd.read_csv('../find-my-landlord-atx-2/combined_results.csv')
del df_fill['Unnamed: 0']
df_fill = df_fill.merge(pd.DataFrame(df_fill.Loc.str.split(',',expand=True)),left_index=True,right_index=True)
df_fill.Addres_m.fillna(df_fill.Address,inplace=True)
df_fill.rename(index=df_fill.Idx,inplace=True)
clean_up(df_fill,cols=[0,1,'Addres_m'])
df_fill.columns = ['Address','X','Y']
df_tcad.X_x.fillna(df_fill.X,inplace=True)
df_tcad.Y_x.fillna(df_fill.Y,inplace=True)
df_tcad = geopandas.GeoDataFrame(df_tcad)
df_tcad.X_x.fillna(df_tcad.geometry_y.centroid.x,inplace=True)
df_tcad.Y_x.fillna(df_tcad.geometry_y.centroid.y,inplace=True)

#Handle missing unit estimates for residential buildings
#Assume O1 props are 1 unit
df_tcad.units_x = np.where(df_tcad.code2=='O1',1,df_tcad.units_x)
df_tcad.units_x = np.where(df_tcad.type1=='Detail Only',1,df_tcad.units_x)
#Use land use data to caluclate units
df_tcad.units_x = np.where(((df_tcad.land_use==100)|(df_tcad.land_use==160))&(df_tcad.units_x.isnull()),1,df_tcad.units_x)
df_tcad.units_x = np.where((df_tcad.land_use==150)&(df_tcad.units_x.isnull()),2,df_tcad.units_x)
df_tcad.units_x = np.where((df_tcad.land_use==210)&(df_tcad.units_x.isnull()),4,df_tcad.units_x)
#Over write wrong unit estimates ie anything <5 units that cost more then 10m
df_tcad.units_x = np.where((df_tcad.value>10000000)&(df_tcad.units_x<5),np.nan,df_tcad.units_x)
#Write known column where units are correct or rather better estimates 
df_tcad['known'] = np.where(df_tcad.units_x.notnull(),True,False)

#Only Residential form now on
res_type = ['DORMITORY HIRISE', 'DORMITORY','APARTMENT   5-25','LUXURY HI-RISE APTS 100+', 'APARTMENT 100+'] 
#df_tcad['res'] = (df_tcad.res | df_tcad.type1.isin(res_type)) 
df_tcad['res'] = (df_tcad.res | df_tcad.type1.isin(res_type) | (df_tcad.type1.str.contains('CONDO',na=False))) 
df_res = df_tcad.loc[df_tcad.res] 

#Impute by zip and appraisal value 
dfs = df_res.groupby('zip').apply(lambda df: mice(df[['units_x','value','prop_id']].values) if df[['units_x','value','prop_id']].units_x.isnull().any() & ~df[['units_x','value','prop_id']].units_x.isnull().all() else df).apply(lambda df: pd.DataFrame(df))
df_impute_zip = pd.concat(dfs.values)        
#Merge it back and fill it in (smart: if not lower then low estimate from imp data)
df_impute_zip = df_impute_zip.loc[df_impute_zip[0].notnull()][[0,1,2]]
df_impute_zip.columns = ['unit_est','value','prop_id']
df_res = df_res.merge(df_impute_zip,on=['prop_id','value'],how='left')
df_res.units_x.fillna(df_res.unit_est,inplace=True)
df_res.units_x = np.where((df_res.low>df_res.units_x)&(~df_res.known),df_res.low,df_res.units_x)
#Round it and correct 
df_res.units_x = round(df_res.units_x)
df_res.units_x = np.where(df_res.units_x<1, 1, df_res.units_x)

#***^THIS CAN BE IMPROVED LOOK INTO https://scikit-learn.org/stable/auto_examples/impute/plot_missing_values.html#sphx-glr-auto-examples-impute-plot-missing-values-py***
# https://analyticsweek.com/content/iterative-imputation-for-missing-values-in-machine-learning/
