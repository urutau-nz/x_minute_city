# Evaluating access in New Zealand cities


### Add the blocks and boundary
`shp2pgsql -I -s 2193:4269 /file/Research/CivilSystems/data/new_zealand/census/processed/meshblock-2018-generalised.shp block_18 | psql -U postgres -d access_nz_ham -h 132.181.102.2 -p 5001`
`shp2pgsql -I -s 27200:4269 /file/Research/CivilSystems/data/new_zealand/hamilton/council_zones/UA_TA_Hamilton_CC.shp boundary | psql -U postgres -d access_nz_ham -h 132.181.102.2 -p 5001`


### Code to setup routing code and conduct routing
```
import init_osrm
import query
from config import *

states = ['il','md','fl', 'co', 'mi', 'la', 'ga', 'or', 'wa', 'tx']

for state in states:
  init_osrm.main(state)
  query.main(state)
```


### Adding meshblock data to database
Download appropriate meshblock shapefile. For example NZ 2018 census meshblocks: https://datafinder.stats.govt.nz/layer/92197-meshblock-2018-generalised/

Find WKID:
shp2pgsql -I -s 2193 meshblock-2018-generalised.shp block | psql -U postgres -d access_nz_ham -h 132.181.102.2 -p 5001

Add city boundaries:
http://archive.stats.govt.nz/browse_for_stats/Maps_and_geography/Geographic-areas/digital-boundary-files.aspx#annual
