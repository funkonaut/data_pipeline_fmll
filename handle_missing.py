########################
###  HANDLE MISSING  ###
########################
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
df_fill = pd.read_csv('./combined_results.csv')
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

#ESTIMATE THE REST
#Anything under 100k is assumed 1 unit
df_tcad.units_x = np.where((df_tcad.value<100000)&(df_tcad.units_x.isnull()),1,df_tcad.units_x)
#Take high end of ranges in improvement type data
df_tcad.units_x.fillna(df_tcad.high,inplace=True)
df_tcad.units_x.fillna(df_tcad.low,inplace=True) 

#calculate avg unit cost for known residential units 
##will I get a more accurate answer if I look at 2016 unit cost? or just assume 2016 numbers are mostly consitent?
df_known = df_tcad.loc[df_tcad.known]
##get each props unit cost
df_known['unit_cost'] = df_known.value/df_known.units_x
##group by to calculate average cost per prop type in a sub_div
df_known['avg_unit_cost'] = df_known.groupby(['sub_div','type1'])['unit_cost'].transform('mean')
df_known['avg_unit_cost_zip'] = df_known.groupby(['zip'])['unit_cost'].transform('mean')
clean_up(df_known,['prop_id','avg_unit_cost','avg_unit_cost_zip'])
df_tcad = df_tcad.merge(df_known,on='prop_id',how='left').drop_duplicates('prop_id')
df_tcad.avg_unit_cost = df_tcad.groupby(['sub_div','land_use'])['avg_unit_cost'].transform('ffill')
df_tcad.avg_unit_cost = df_tcad.groupby(['sub_div','land_use'])['avg_unit_cost'].transform('bfill')
df_tcad.avg_unit_cost_zip = df_tcad.groupby(['zip'])['avg_unit_cost_zip'].transform('ffill')
df_tcad.avg_unit_cost_zip = df_tcad.groupby(['zip'])['avg_unit_cost_zip'].transform('bfill')
df_tcad.units_x.fillna(round(df_tcad.value/df_tcad.avg_unit_cost),inplace=True)
df_tcad.units_x.replace(0,1,inplace=True) #round anything that is 0 up to 1
##fill in what wasnt caught by subdiv and land_use groupings with zip groupings
df_tcad.units_x.fillna(round(df_tcad.value/df_tcad.avg_unit_cost_zip),inplace=True)
df_tcad.units_x.replace(0,1,inplace=True) #round anything that is 0 up to 1
