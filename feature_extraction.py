########################
###Feature extraction###
########################
#Unit number from improvement data
df_units = extract_nums(df_units,'type1')
df_units.columns = ['type1','prop_id','low','high','trash']
del df_units['trash']
df_units.replace('',0,inplace=True)
df_units['units'] = np.where((df_units.low<5)&(df_units.high == 0),df_units.low,0)
single = [ 'MOHO SINGLE PP','TOWNHOMES','MOHO SINGLE REAL','CONDO (STACKED)'] 
double = ['GARAGE APARTMENT','Accessory Dwelling Unit','Accessory Dwelling Unit (','MOHO DOUBLE REAL', 'MOHO DOUBLE PP']
triple = 'TRIPLEX'
quad = 'FOURPLEX'
for key in single: df_units['units'] = df_units.apply(lambda row: 1 if row.type1 == key else row['units'], axis=1) 

for key in double: df_units['units'] = df_units.apply(lambda row: 2 if row.type1 == key else row['units'], axis=1) 

df_units['units'] = df_units.apply(lambda row: 3 if row.type1 == triple else row['units'], axis=1) 
df_units['units'] = df_units.apply(lambda row: 4 if row.type1 == quad else row['units'], axis=1) 

#df_units replace unit estimate with sum of any additional units added on
#df_units['units'] = df_units.groupby('prop_id').unit.transform('sum')
#del df_units['unit']
#df_unit.unit.replace(0,np.nan,inplace=True)
#just take high estimates
#df_units.units = np.where((df_units.high==0)&(df_units.low!=0),df_units.low,df_units.units)
#df_units.units = np.where((df_units.high!=0)&(df_units.low!=0),df_units[['low','high']].mean(axis=1),df_units.units)
#Drop duplicates of lower number
df_units.sort_values('units',ascending=False,inplace=True)
df_units.drop_duplicates('prop_id',inplace=True)
#Anything that is known from type should over ride the 2016 estimates (this could be false...)
df_units['units_from_type'] = np.where(df_units.units!=0, True, False)
df_units['est_from_type'] = np.where(df_units.units==0, True, False)

#Extract new properties
extract_new_props(df_tcad,'deed')

extract_coor(gdf)
extract_coor(gdf_16)
coor_to_geometry(df_locs)
coor_to_geometry(df_code,['LONGITUDE','LATITUDE'])

