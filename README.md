# Evaluating access in New Zealand cities


### Add the blocks and boundary
`shp2pgsql -I -s 2193:4326 /file/Research/CivilSystems/data/new_zealand/census/processed/meshblock-2018-generalised.shp block_18 | psql -U postgres -d access_nz_ham -h 132.181.102.2 -p 5001`
`shp2pgsql -I -s 27200:4326 /file/Research/CivilSystems/data/new_zealand/hamilton/council_zones/UA_TA_Hamilton_CC.shp boundary | psql -U postgres -d access_nz_ham -h 132.181.102.2 -p 5001`


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
