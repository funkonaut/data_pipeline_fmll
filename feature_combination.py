########################
### Feature combine  ###
########################
#Combine Units:
df_tcad = merge_extraction(dfs=[df_tcad,df_units,gdf_16],val=['dba','type1','units','low','high','units_from_type','est_from_type','shape_area'])
replace_nan(df_tcad,['units_x','units_y','low','high'],val=0,reverse=True)
#Don't fill in any unit estimates from improvement data yet (will do that in handle missing) (the low high estimate ranges)
df_tcad.units_y = np.where(df_tcad.est_from_type, np.nan, df_tcad.units_y)
#Fill in missing in known data from 2016 with type data
df_tcad.units_x.fillna(df_tcad.units_y,inplace=True)
#Known units column
df_tcad['known']= np.where(df_tcad.units_x.notnull(), True,False)
#Where type data is larger then 2016 take the new value
#df_tcad.units_x = np.where((df_tcad.units_x < df_tcad.units_y), df_tcad.units_y, df_tcad.units_x)
#Get rid of type values
del df_tcad['units_y']

#Combine Locations:
df_tcad = merge_extraction(dfs=[df_tcad,gdf,df_locs],on='prop_id',val=['land_use','X','Y','geometry','shape_area'])
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
#Known location column
df_tcad['known_loc']= np.where(df_tcad.X_x.notnull(), True,False)

#Residential criteria
res = ['A1','A2','A3','A4','A5','B1','B2','B3','B4','E2','M1','XA']
res_type = ['ALT LIVING CTR', 'DORMITORY HIRISE', 'DORMITORY', 'APARTMENT   5-25', 'LUXURY HI-RISE APTS 100+', 'APARTMENT 100+', 'GARAGE APARTMENT', 'Accessory Dwelling Unit' 'FOURPLEX', 'MOHO DOUBLE PP'] #got rid of detail only
res_code =  ['100','113','150','160','210','220','230','240','330']
df_tcad['res'] = df_tcad.code2.isin(res)
df_tcad['res'] = (df_tcad.res | (df_tcad.hs=='T') |  df_tcad.type1.isin(res_type) | (df_tcad.type1.str.contains('CONDO',na=False)) | (df_tcad.type1.str.contains('DWELLING',na=False)) |  (df_tcad.desc.str.contains('APARTMENT',na=False)) |  (df_tcad.desc.str.contains('APARTMENT',na=False)) | df_tcad.type1.str.contains('APARTMENT',na=False) | df_tcad.type1.str.contains('APT',na=False) | df_tcad.type1.str.contains('DORM',na=False) | (df_tcad.type1.str.contains('MOHO',na=False)))
#df_tcad['res'] = (df_tcad.res | df_tcad.type1.isin(res_type) | (df_tcad.type1.str.contains('CONDO',na=False)) | (df_tcad.type1.str.contains('DWELLING',na=False)) | ((df_tcad.desc.str.contains('CONDO',na=False))&(~df_tcad.desc.str.contains('CONDO',na=False))) | (df_tcad.desc.str.contains('APARTMENT',na=False))))

#apts = df_tcad.loc[ df_tcad.type1.str.contains('APARTMENT',na=False) | df_tcad.type1.str.contains('APT',na=False) | df_tcad.type1.str.contains('DORM',na=False)| (df_tcad.type1.str.contains('CONDO',na=False))]

