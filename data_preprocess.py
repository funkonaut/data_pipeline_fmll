########################
### Data pre-process ###
########################
#Clean up gdfs
clean_up(gdf,['parcel_id_','created_by','date_creat','time_creat','general_la','modified_b','date_modif','time_modif','objectid','land_use_i'],True)
clean_up(gdf_16,['py_owner_i','shape_area','lotsize','units','dba','owner','prop_id','situs','geometry'])

combine_string_cols(df_tcad,['st_number','prefix','st_name','suffix'],'ADDRESS_LONG')
combine_string_cols(df_tcad,['st_number','prefix','st_name','suffix','city','zip'],'address')
combine_string_cols(df_tcad,['mail_add_1','mail_add_2','mail_add_3','mail_city','mail_state','mail_zip'],'owner_add')
replace_nan(df_tcad,['address','owner_add'],val='      ',reverse=True)

#Cleanup address of df_aff2 by stripping white spaces
df_tcad.address = df_tcad.address.str.rstrip()
df_tcad.address = df_tcad.address.str.lstrip()
df_tcad.address = df_tcad.address.str.replace(' +',' ')
df_tcad.owner_add = df_tcad.owner_add.str.rstrip()
df_tcad.owner_add = df_tcad.owner_add.str.lstrip()
df_tcad.owner_add = df_tcad.owner_add.str.replace(' +',' ')

#Convert numberic data to ints st_number will lose some unit info or fraction info 
df_tcad['zip']       = convert_to_numeric(df_tcad,'zip')
df_tcad['mail_zip']  = convert_to_numeric(df_tcad,'mail_zip')
df_tcad['geo_id']    = convert_to_numeric(df_tcad,'geo_id')
gdf_16['prop_id']    = gdf_16['prop_id'].astype(int) 
gdf['property_i']    = convert_to_numeric(gdf,'property_i')

#****MAYBE CAN GET RID OF MORE**** Get rid of rows with no useful info
gdf_16 = gdf_16.loc[gdf_16.prop_id!=0]
gdf    = gdf.loc[gdf.property_i!=0]
gdf.rename(columns={ gdf.columns[1]: "prop_id" }, inplace = True)

#Todo sum up unit count and use this data to fill in missing values for locations and units Cleanup construction permit data only residential
df_con = df_con.loc[(df_con['Permit Class Mapped']=='Residential')]
#Get rid of rows with no useful info
df_con = df_con.loc[df_con['TCAD ID'].notnull()&df_con['Latitude'].notnull()&df_con['Housing Units'].notnull()]
df_con = df_con.loc[df_con['Work Class']!='Demolition']
df_con['TCAD ID'] = extract_num(df_con,'TCAD ID')
keep = ['TCAD ID','Latitude','Longitude']
df_con = df_con[keep]
df_con.drop_duplicates('TCAD ID',inplace = True)

#Eviction Data
#Get rid of rows with no useful info around 500 just case numbers or nothing at all
df_evict.drop(df_evict.loc[df_evict.Lat.isnull() & df_evict['Property ID'].isnull()].index,inplace=True)
clean_up(df_evict,['Unnamed: 12' , 'Unnamed: 13' , 'Unnamed: 14'],delete=True)
