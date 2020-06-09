'''
Script for adding destinations when the dest_table has already been made. Dests must be in csv files.
e.g https://www.educationcounts.govt.nz/data-services/directories/list-of-nz-schools#
This script has been created with NZ schools in mind but may be adapted for other dest types.
'''
#for downtown:
def add_downtown(state):
    '''adds a point for downtown, lat and lon must be specified'''
    df = pd.DataFrame(columns=['id', 'dest_type', 'name', 'Latitude', 'Longitude'])
    df['id'] = list(range(len(df)))
    df.set_index('id', inplace=True)
    df_down.loc[0] = ['downtown', 'downtown', -37.7870, 175.2793]
    #then do same with gpd as below


from config import *


def append_dests(state):
    '''opens and appends new dest'''
    #initialize db connection
    db, context = cfg_init(state)
    filename = '/homedirs/dak55/resilience_equity/data/census/primary_school_ham.csv'
    df = pd.read_csv(filename, encoding = "ISO-8859-1", skiprows=15)

    #extraact and format data so it is the same form as destinations
    df = df[['Org Name', 'Latitude', 'Longitude']]
    df['dest_type'] = 'primary_school'
    df = df.rename(columns={'Org Name':'name'})
    df['id'] = list(range(len(df)))
    df.set_index('id', inplace=True)
    cols = ['dest_type', 'name', 'Latitude', 'Longitude']
    df = df[cols]

    #convert to gdf and format to send to sql
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))
    gdf.drop(['Latitude', 'Longitude'], axis=1, inplace=True)
    gdf['geom'] = gdf['geometry'].apply(lambda x: WKTElement(x.wkt, srid=4269))
    gdf.drop('geometry', 1, inplace=True)
    gdf.to_sql('destinations', engine, if_exists='append', index=False, dtype={'geom': Geometry(geometry_type='POINT', srid= 4269)})

state = input('State: ')
