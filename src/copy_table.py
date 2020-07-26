'''
copies a table from one database to another
'''

from config import *
from_state = input("State transferring from: ")
table_name = input("table name: ")
db_from, context_from = cfg_init(from_state)
to_state = input("State transferring too: ")
db_to, context_to = cfg_init(to_state)
type_gdf = input("gdf True or False? ")
if type_gdf == True:
    sql = "SELECT * FROM {}".format(table_name)
    df = pd.read_sql(sql, db_from['con'])
    df.to_sql(table_name, db_to['engine'], if_exists='replace')
elif type_gdf == False:
    sql = "SELECT * FROM {}".format(table_name)
    gdf = gpd.GeoDataFrame.from_postgis(sql, db_from['con'], geom_col='geom')
    gdf.to_sql(table_name, db_to['engine'], if_exists='replace')





#method for geospatial tables
gdf_old = gpd.GeoDataFrame.from_postgis("SELECT * FROM destinations", db['con'], geom_col='geom')
#change connection to new database
gdf_old['geom'] = gdf_old['geom'].apply(lambda x: WKTElement(x.wkt, srid=4269))
gdf_old.to_sql('helloworld', db['engine'], if_exists='append', index=False, dtype={'geom': Geometry(geometry_type='POINT', srid= 4269)})
