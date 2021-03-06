'''
Init the database
Query origins to dests in OSRM
'''
# user defined variables
par = True
par_frac = 0.9
# transport_mode = 'walking'#'driving'

from config import *
logger = logging.getLogger(__name__)
import math
import os.path
# import osgeo.ogr
import io
import shapely
from geoalchemy2 import Geometry, WKTElement
import requests
from sqlalchemy.types import Float, Integer
if par == True:
    import multiprocessing as mp
    from joblib import Parallel, delayed
    from requests.adapters import HTTPAdapter
    from requests.packages.urllib3.util.retry import Retry

def main(state, transport_mode, append=False):
    '''
    set up the db tables I need for the querying
    '''
    db, context = cfg_init(state)

    # init the destination tables
    #create_dest_table(db, context)

    # query the distances
    query_points(db, context, transport_mode, append)

    # close the connection
    db['con'].close()
    logger.info('Database connection closed')

    # email completion notification
    #utils.send_email(body='Querying {} complete'.format(context['city']))


def create_dest_table(db, context):
    '''
    create a table with the destinations
    '''
    # db connections
    con = db['con']
    engine = db['engine']
    cursor = db['con'].cursor()
    # destinations and locations
    types = context['services']
    # import the csv's
    gdf = gpd.GeoDataFrame()
    for dest_type in types:
        files = '/homedirs/dak55/resilience_equity/data/{}/{}_{}.shp'.format(context['city_code'], dest_type, context['city_code'])
        df_type = gpd.read_file('{}'.format(files))
        # df_type = pd.read_csv('data/destinations/' + dest_type + '_FL.csv', encoding = "ISO-8859-1", usecols = ['id','name','lat','lon'])
        if df_type.crs['init'] != 'epsg:4269':
            # project into lat lon
            df_type = df_type.to_crs({'init':'epsg:4269'})
        df_type['dest_type'] = dest_type
        gdf = gdf.append(df_type)

    # set a unique id for each destination
    gdf['id'] = range(len(gdf))
    # prepare for sql
    gdf['geom'] = gdf['geometry'].apply(lambda x: WKTElement(x.wkt, srid=4269))
    #drop all columns except id, dest_type, and geom
    gdf = gdf[['id','dest_type', 'Name', 'geom']]
    gdf = gdf.rename(columns={'Name':'name'})
    # set index
    gdf.set_index(['id','dest_type'], inplace=True)

    # export to sql
    gdf.to_sql('destinations', engine, if_exists='replace', dtype={'geom': Geometry('POINT', srid= 4269)})

    # update indices
    cursor = con.cursor()
    queries = ['CREATE INDEX "dest_id" ON destinations ("id");',
            'CREATE INDEX "dest_type" ON destinations ("dest_type");']
    for q in queries:
        cursor.execute(q)

    # commit to db
    con.commit()


def query_points(db, context, transport_mode, append):
    '''
    query OSRM for distances between origins and destinations
    '''
    # connect to db
    cursor = db['con'].cursor()

    # get list of all origin ids
    sql = "SELECT block_18.sa12018_v1, block_18.geom FROM block_18, boundary WHERE ST_Intersects(block_18.geom, boundary.geom)"
    orig_df = gpd.GeoDataFrame.from_postgis(sql, db['con'], geom_col='geom')
    orig_df['x'] = orig_df.geom.centroid.x
    orig_df['y'] = orig_df.geom.centroid.y
    # drop duplicates
    orig_df.drop('geom',axis=1,inplace=True)
    orig_df.drop_duplicates(inplace=True)
    # set index
    orig_df = orig_df.set_index('sa12018_v1')

    # get list of destination ids
    sql = "SELECT * FROM destinations"
    dest_df = gpd.GeoDataFrame.from_postgis(sql, db['con'], geom_col='geom')
    dest_df = dest_df.set_index('id')
    dest_df['lon'] = dest_df.geom.centroid.x
    dest_df['lat'] = dest_df.geom.centroid.y

    # list of origxdest pairs
    origxdest = pd.DataFrame(list(itertools.product(orig_df.index, dest_df.index)), columns = ['id_orig','id_dest'])
    origxdest['distance'] = None
    origxdest['duration'] = None

    # df of durations, distances, ids, and co-ordinates
    origxdest = execute_table_query(origxdest, orig_df, dest_df, context, transport_mode)

    # add df to sql
    logger.info('Writing data to SQL')
    write_to_postgres(origxdest, db, 'distance_duration', append)
    # origxdest.to_sql('distance_duration', con=db['engine'], if_exists='replace', index=False, dtype={"distance":Float(), "duration":Float(), 'id_dest':Integer()}, method='multi')
    logger.info('Distances written successfully to SQL')
    logger.info('Updating indices on SQL')

    if not append:
        # update indices
        queries = [
                    'CREATE INDEX "dest_idx" ON distance_duration ("id_dest");',
                    'CREATE INDEX "orig_idx" ON distance_duration ("id_orig");'
                    ]
        for q in queries:
            cursor.execute(q)

    # commit to db
    db['con'].commit()
    logger.info('Query Complete')

def write_to_postgres(df, db, table_name, append):
    ''' quickly write to a postgres database
        from https://stackoverflow.com/a/47984180/5890574'''
    df.id_orig = df.id_orig.astype(int)
    if not append:
        df.head(0).to_sql(table_name, db['engine'], if_exists='replace',index=False) #truncates the table

    conn = db['engine'].raw_connection()
    cur = conn.cursor()
    output = io.StringIO()
    df.to_csv(output, sep='\t', header=False, index=False)
    output.seek(0)
    cur.copy_from(output, table_name, null="") # null values become ''
    conn.commit()


def execute_table_query(origxdest, orig_df, dest_df, context, transport_mode):
    # Use the table service so as to reduce the amount of requests sent
    # https://github.com/Project-OSRM/osrm-backend/blob/master/docs/http.md#table-service

    batch_limit = 10000

    dest_n = len(dest_df)
    orig_n = len(orig_df)
    orig_per_batch = int(batch_limit/dest_n)
    batch_n = math.ceil(orig_n/orig_per_batch)

    #create query string
    base_string = context['osrm_url'] + "/table/v1/{}/".format(transport_mode)

    # make a string of all the destination coordinates
    dest_string = ""
    for j in dest_df.index:
        #now add each dest in the string
        dest_string += str(dest_df.loc[j,'lon']) + "," + str(dest_df.loc[j,'lat']) + ";"
    #remove last semi colon
    dest_string = dest_string[:-1]

    # options string
    options_string_base = '?annotations=duration,distance'

    # loop through the sets of
    orig_sets = [(i, min(i+orig_per_batch, orig_n)) for i in range(0,orig_n,orig_per_batch)]

    # create a list of queries
    query_list = []
    for i in orig_sets:
        # make a string of all the origin coordinates
        orig_string = ""
        orig_ids = range(i[0],i[1])
        for j in orig_ids:
            #now add each dest in the string
            orig_string += str(orig_df.x[j]) + "," + str(orig_df.y[j]) + ";"
        # make a string of the number of the sources
        source_str = '&sources=' + str(list(range(len(orig_ids))))[1:-1].replace(' ','').replace(',',';')
        # make the string for the destinations
        dest_idx_str = '&destinations=' + str(list(range(len(orig_ids), len(orig_ids)+len(dest_df))))[1:-1].replace(' ','').replace(',',';')
        # combine and create the query string
        options_string = options_string_base + source_str + dest_idx_str
        query_string = base_string + orig_string + dest_string + options_string
        # append to list of queries
        query_list.append(query_string)

    # # Table Query OSRM in parallel
    if par == True:
        #define cpu usage
        num_workers = np.int(mp.cpu_count() * par_frac)
        #gets list of tuples which contain 1list of distances and 1list
        results = Parallel(n_jobs=num_workers)(delayed(req)(query_string) for query_string in tqdm(query_list))
    else:
        results = []
        for query_string in tqdm(query_list):
             results.append(req(query_string))

    # get the results in the right format
    dists = [l for orig in results for l in orig[0]]
    durs = [l for orig in results for l in orig[1]]
    origxdest['distance'] = dists
    origxdest['duration'] = durs
    origxdest['mode'] = transport_mode

    return(origxdest)

def req(query_string):
    response = requests.get(query_string).json()
    temp_dist = [item for sublist in response['distances'] for item in sublist]
    temp_dur = [item for sublist in response['durations'] for item in sublist]
    return temp_dist, temp_dur


if __name__ == "__main__":
    state = input('State: ')
    logger.info('query.py code invoked')
    main(state)
