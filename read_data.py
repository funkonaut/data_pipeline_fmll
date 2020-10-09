##########################
###Read in data sources###
##########################
#Appraisal data for Travis county: https://www.traviscad.org/reports-request/
col_specs = [(12,17),(2608,2609),(2033,2058),(2731,2741),(2741,2751),(2751,2761),(1745,1795),(1695,1745),(1675,1685),(1659,1675),(1149,1404),(1915,1930),(1686,1695),(546,596),(0,12),(596, 608),(608,678),(4459,4474),(1039,1049),(1049,1099),(1099,1109),(1109,1139),(1139,1149),(4475,4479),(693,753),(753,813),(813,873),(873,923),(923,974),(978,983),(4135,4175)]
df_tcad = pd.read_fwf('../data_laundry/TCAD/PROP.TXT',col_specs)
df_tcad.columns = ['type','hs','deed','code','code2','code3','lot','block','sub_div','acre','desc','value','hood','geo_id','prop_id', 'py_owner_i','prop_owner','st_number','prefix','st_name','suffix','city','zip','unit_num','mail_add_1','mail_add_2','mail_add_3','mail_city','mail_state','mail_zip','DBA']

#Improvement data (type and property ID
col_specs2 =[(38,63),(0,12)]
df_units = pd.read_fwf('../data_laundry/TCAD/IMP_INFO.TXT',col_specs2)
df_units.columns = ['type1','prop_id']

#Land Use inventory for Travis county: https://data.austintexas.gov/Locations-and-Maps/Land-Use-Inventory-Detailed/fj9m-h5qy
gdf = geopandas.read_file('../data_laundry/Land Use Inventory Detailed/geo_export_616600a6-8553-4356-9edc-37cc824adb97.shp')

#Land Database from 2016 https://data.austintexas.gov/Building-and-Development/Land-Database-2016/nuca-fzpt
gdf_16 = geopandas.read_file('../data_laundry/Land Database 2016/geo_export_b2aa6a63-5bbb-45b4-8529-cd073f67ad2d.shp')
#Code complaint cases
df_code = pd.read_csv('../data_laundry/Austin_Code_Complaint_Cases.csv')
df_covid = pd.read_csv('../data_laundry/Austin_Code_COVID-19_Complaint_Cases.csv')
df_covid = df_covid.loc[df_covid.TYPEOFCOMPLAINT=='Eviction']

#COA city council
gdfdist = geopandas.read_file('../data_laundry/districts/geo_export_74417697-1c4c-4575-bf46-90c0ce62509c.shp')

#Location data
df_locs = pd.read_csv('../data_laundry/R000258-082120.csv')
df_locs.columns = ['PID_10','prop_id','X','Y']

#Todo incorporate Construction permits
df_con = pd.read_csv('../data_laundry/Issued_Construction_Permits.csv')

#Eviciton Data
df_evict = pd.read_csv('../data_laundry/eviction_data_9_24.csv')
#Social Vulnerability score
gdf_sv = geopandas.read_file('../data_laundry/A2SI_SVI/A2SI_SVI.shp')
