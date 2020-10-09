########################
###  HANDLE MISSING  ###
########################
#Drop duplicates that were introduced in merge extraction
df_tcad.drop_duplicates('prop_id',inplace=True)
#Fill out known values for location
df_tcad['known_loc'] = np.where(df_tcad.X_x.notnull(),True,False)

#Fill in missing geometry is this working correctly? Various locations and somethings getting filled that are not really the same?
df_tcad.shape_area_x.fillna(df_tcad.shape_area_y, inplace=True)
df_tcad.geometry_y = df_tcad.groupby('address').geometry_y.transform('ffill')
df_tcad.geometry_y = df_tcad.groupby('address').geometry_y.transform('bfill')
df_tcad.geometry_y = df_tcad.groupby(['st_name','st_number']).geometry_y.transform('ffill')
df_tcad.geometry_y = df_tcad.groupby(['st_name','st_number']).geometry_y.transform('bfill')
df_tcad.land_use = df_tcad.groupby('address').land_use.transform('ffill')
df_tcad.land_use = df_tcad.groupby('address').land_use.transform('bfill')
df_tcad.land_use = df_tcad.groupby(['st_name','st_number']).land_use.transform('ffill')
df_tcad.land_use = df_tcad.groupby(['st_name','st_number']).land_use.transform('bfill')
df_tcad.shape_area_x = df_tcad.groupby('address').shape_area_x.transform('ffill')
df_tcad.shape_area_x = df_tcad.groupby('address').shape_area_x.transform('bfill')
df_tcad.shape_area_x = df_tcad.groupby(['st_name','st_number']).shape_area_x.transform('ffill')
df_tcad.shape_area_x = df_tcad.groupby(['st_name','st_number']).shape_area_x.transform('bfill')
del df_tcad['geometry_x']
del df_tcad['shape_area_y']

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

#Handle missing DBA's
df_tcad.DBA.fillna(df_tcad.dba,inplace=True)
#df_tcad.DBA.fillna(clean_string(df_tcad,'mail_add_1'),inplace=True)

#Handle missing unit estimates for residential buildings
#Use land use data to caluclate units
df_tcad.units_x = np.where(((df_tcad.land_use==100)|(df_tcad.land_use==160))&(df_tcad.units_x.isnull()),1,df_tcad.units_x)
df_tcad.units_x = np.where((df_tcad.land_use==150)&(df_tcad.units_x.isnull()),2,df_tcad.units_x)
df_tcad.units_x = np.where((df_tcad.land_use==210)&(df_tcad.units_x.isnull()),4,df_tcad.units_x)
#Over write wrong unit estimates ie anything <5 units that cost more then 10m
df_tcad.units_x = np.where((df_tcad.value>10000000)&(df_tcad.units_x<5),np.nan,df_tcad.units_x)
##Write known column where units are correct (from 2016 or improvement type)
df_tcad['known'] = np.where(df_tcad.units_x.notnull(),True,False)

#Fill in estimates from improvement ranges
df_tcad.units_x.fillna(df_tcad.low,inplace=True)
#Anything with over 9999 units is sus
df_tcad.units_x = np.where(df_tcad.units_x>9999,np.nan,df_tcad.units_x)

#Impute by zip and appraisal value for all tcad data 
dfs = df_tcad.groupby(['zip','res']).apply(lambda df: mice(df[['units_x','value','prop_id']].values) if df[['units_x','value','prop_id']].units_x.isnull().any() & ~df[['units_x','value','prop_id']].units_x.isnull().all() else df).apply(lambda df: pd.DataFrame(df))
df_impute_zip = pd.concat(dfs.values)        
#Merge it back and fill it in (smart: if not lower then low estimate from imp data)
df_impute_zip = df_impute_zip.loc[df_impute_zip[0].notnull()][[0,1,2]]
df_impute_zip.columns = ['unit_est','value','prop_id']
df_tcad = df_tcad.merge(df_impute_zip,on=['prop_id','value'],how='left')
#df_tcad.units_x.fillna(df_tcad['unit_est'],inplace=True)
##Round it and correct 
#df_tcad.units_x = round(df_tcad.units_x)
#df_tcad.units_x = np.where(df_tcad.units_x<1, 1, df_tcad.units_x)
##Fill in with property unit estimations on ly where the low of the range estimate is higher then the imputated value
#df_tcad.units_x = np.where((df_tcad.low>df_tcad.units_x)&(~df_tcad.known),df_tcad.low,df_tcad.units_x)
#***^THIS CAN BE IMPROVED LOOK INTO https://scikit-learn.org/stable/auto_examples/impute/plot_missing_values.html#sphx-glr-auto-examples-impute-plot-missing-values-py***
# https://analyticsweek.com/content/iterative-imputation-for-missing-values-in-machine-learning/
