'''
Exports a gjson with the polygons
Exports a csv with location: id, lat, lon, dest_type
Exports a csv with orig_id, duration, dest_type, transport_mode
'''
state = 'nz_ham'

from config import *
from shapely.geometry import Point

db, context = cfg_init(state)
con = db['con']
city_code = context['city_code']

###
# blocks
###

def duration():
    '''
    Exports nearest_in_time as a shapefile after removing blocks with 0 population
    '''
    #creates df of geoid10 indexes
    sql = "SELECT block_18.sa12018_v1, block_18.geom FROM block_18, boundary WHERE ST_Intersects(block_18.geom, boundary.geom)"
    orig_df = gpd.GeoDataFrame.from_postgis(sql, con, geom_col='geom')
    #sorts and indexes by geoid10 of the blocks
    orig_df['gid'] = orig_df.sa12018_v1.astype(np.int)
    orig_df = orig_df.sort_values(by='gid', axis=0, ascending=True, inplace=False, kind='quicksort', na_position='last')
    orig_df = orig_df.set_index('gid')

    #opening total population stats for each block
    sql = """SELECT population, gid FROM census_18"""
    demo_df = pd.read_sql(sql, con)
    demo_df = demo_df.dropna(axis=0)
    demo_df.gid = demo_df.gid.astype(np.int)
    #orders by geoid and sets it as the index
    demo_df = demo_df.sort_values(by='gid', axis=0, ascending=True, inplace=False, kind='quicksort', na_position='last')
    demo_df = demo_df.set_index('gid')
    #adds population data to blocks
    orig_df['population'] = demo_df.population

    #removing all rows where population is 0
    orig_df = orig_df.drop(orig_df[orig_df.population == 0].index)

    #exports file to my folder
    with open('/homedirs/tml62/x_minute_city/data/block_{}.geojson'.format(city_code), "wt") as tf:
        blocks = orig_df.drop(columns=['population'])
        tf.write(blocks.to_json())

    # imports the distances
    sql = '''
            SELECT dur.id_orig, dest.dest_type, dur.mode, MIN(dur.duration)
            FROM distance_duration dur
            JOIN destinations dest on dest.id = dur.id_dest
            GROUP BY dur.id_orig, dest.dest_type, dur.mode;
            '''
    df = pd.read_sql(sql, con)
    #sorts and indexes by geoid10 of the blocks
    df = df.sort_values(by='id_orig', axis=0, ascending=True, inplace=False, kind='quicksort', na_position='last')
    df = df.pivot_table(index=['id_orig','mode'],columns='dest_type', values='min')

    # merge
    orig_df = pd.merge(orig_df, df, left_index=True, right_index=True)

    # drop extra stuff
    # orig_df = orig_df.drop(columns=['geom'])
    # orig_df.index.rename('gid', inplace=True)
    orig_df.to_csv('/homedirs/tml62/x_minute_city/data/duration_{}.csv'.format(city_code))

def destinations():
    # export all destinations as csv
    sql = "SELECT * FROM destinations"
    service_df = gpd.GeoDataFrame.from_postgis(sql, con, geom_col='geom')
    service_df['lon'] = service_df.geom.x
    service_df['lat'] = service_df.geom.y
    df = pd.DataFrame(service_df.drop(columns=['geom','index']))
    df.to_csv('/homedirs/tml62/x_minute_city/data/destinations_{}.csv'.format(city_code))

    con.close()
