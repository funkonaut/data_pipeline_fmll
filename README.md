# data\_pipeline\_fmll
## Data pipeline for find my landlord project.

## Run
functions.py > read\_data.py > data\_preprocess.py > feature\_extraction.py > feature\_combination.py > handle\_missing.py (calls geocode.py) > landlord\_find.py > dedupe.py > affiliate\_code.py 

## See it live!
Check it out [here](https://funkonaut.github.io/find-my-landlord-atx).

## Methodolgy 
Rental Property Determination Methodology: 

### Data sets
The Find My Landlord dataset is comprised of multiple data sets:
- [Travis County appraisal district (TCAD) property data](https://www.traviscad.org/reports-request/) (appraisal roll export)
- [TCAD improvement data](https://www.traviscad.org/reports-request/) (appraisal roll export)
- A [land use inventory shape file](https://data.austintexas.gov/Locations-and-Maps/Land-Use-Inventory-Detailed/fj9m-h5qy) for Travis County https://data.austintexas.gov/Locations-and-Maps/Land-Use-Inventory-Detailed/fj9m-h5qy
- A [2016 Land database](https://data.austintexas.gov/Building-and-Development/Land-Database-2016/nuca-fzpt) from the city of Austin 
- [US census geocoder](https://geocoding.geo.census.gov)

### Unit counts
From these datasets information was extracted and compiled inorder to determine residential rental properties. Unit counts were extracted from the TCAD improvement type data as follows:
- MOHO SINGLE PP,TOWNHOMES,MOHO SINGLE REAL,CONDO (STACKED) marked as 1 unit
- GARAGE APARTMENT,Accessory Dwelling Unit,Accessory Dwelling Unit (,MOHO DOUBLE REAL, MOHO DOUBLE PP marked as two units
- TRIPLEX marked as three units
- FOURPLEX marked as four units

Other unit data was extracted from the 2016 land database which is the only complete official document by the city of unit counts for residential properties. The unit counts known from improvement type took precedence over the 2016 unit counts where they conflicted. Missing unit data was imputed using MICE algorithm using known units value as features and grouping properties by zip code and whether or not they were residential, these were marked as estimates so as not to display incorrect information publicly. 

### Residential Property Labeling
Properties were also determined to be residential by looking at land use and zoning data in TCAD property and improvements tables and the Travis county land use inventory:
- A1,A2,A3,A4,A5,B1,B2,B3,B4,E2,M1,XA land codes were marked as residential
- ALT LIVING CTR, DORMITORY HIRISE, DORMITORY, APARTMENT   5-25, LUXURY HI-RISE APTS 100+, APARTMENT 100+, GARAGE APARTMENT, Accessory Dwelling Unit FOURPLEX, MOHO DOUBLE PP improvement building types were marked as residential
- As well improvement building types that contained the words: CONDO, DWELLING, APARTMENT, APT, DORM, or MOHO were marked as residential
- Properties that had descriptions in the TCAD property table that contained the words: APARTMENT 
- 100,113,150,160,210,220,230,240,330 land use codes were marked as residential
- Properties that were of building type OFF/RETAIL (SFR),  COMMERCIAL SPACE CONDOS, SM OFFICE CONDO, LG OFFICE CONDO, OFFICE (SMALL),SM STORE <10K SF, STRIP CTR <10000, WAREHOUSE <20000, "MFD COMMCL BLDG", OFFICE LG >35000, MEDICAL OFF <10K, PARKING GARAGE were excluded from residential properties as well.

### Geolocation
Geo location data was extracted from the 2016 data set as well as the land use dataset and missing data was geocoded using the US census geocoding tool.

### Rental Criteria
Inorder to determine if a property was a rental property a property must:
- Not be a residential single unit with a mailing address matching its property address
- It could be owned by a property owner with multiple properties in TCAD (this could let some false positives slip by of folks with multiple residential homes)
- Not have a homestead exemption and be a single unit

Some false positives that slipped by were PO boxes owned by the city and address that were “VARIOUS LOCATIONS” these were dropped as well as a school and a homeowners association building after manual review. 

The resulting list of 80,000+ properties had unit counts and unit count estimates summed and evaluated against census estimates of rental properties within 10% margin of error. 

## Licensing
Please refer to the LICENSE file when using this code or any data produced by running this code. This code and data is distributed without warranty of any kind, implied, expressed or statutory. The owner of this github makes no claims, promises or guarantees about the accuracy, completeness, or adequacy of this information and expressly disclaims liability for any errors and omissions.
