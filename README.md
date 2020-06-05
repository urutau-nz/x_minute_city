# An index for urban inequality:
## Case study on USA supermarket access


psql -h 132.181.102.2 -p 5001 -U postgres -W
#code.interact(local=locals())


`docker run --name osrm-fl -t -i -p 6012:5000 -v /homedirs/man112/osm_data:/data osrm/osrm-backend osrm-routed --algorithm mld --max-table-size 100000 /data/florida-latest.osrm`

init_osrm.main(state)
query.main(state)


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
