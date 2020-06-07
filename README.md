# Evaluating access in New Zealand cities


### Add the origins (statistical area 1) and boundary
`shp2pgsql -I -s 4326:4269 /file/Research/CivilSystems/data/new_zealand/census/raw/2018/statistical-area-1-2018-generalised.shp block_18 | psql -U postgres -d access_nz_ham -h 132.181.102.2 -p 5001`
`shp2pgsql -I -s 27200:4269 /file/Research/CivilSystems/data/new_zealand/hamilton/council_zones/UA_TA_Hamilton_CC.shp boundary | psql -U postgres -d access_nz_ham -h 132.181.102.2 -p 5001`


### Code to setup routing code and conduct routing
```
import init_osrm
import query
from config import *

states = ['nz_ham']#, 'nz_chc']
modes = ['walking', 'cycling']

j = 0
for mode in modes:
  init_osrm.main('nz', mode)
  for state in states:
    query.main(state, mode, append=j)
  j+=1
```
