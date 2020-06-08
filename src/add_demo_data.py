'''

Sorts census csv files and adds desired info to a datatable in access_nz

'''



#Imports

import pickle as pk
import pandas as pd
import numpy as np
import psycopg2
from sqlalchemy.engine import create_engine
from datetime import datetime, timedelta
import itertools
import time
from time import sleep
import progressbar as pb
from tqdm import tqdm
from psycopg2.extensions import register_adapter, AsIs
psycopg2.extensions.register_adapter(np.int64, psycopg2._psycopg.AsIs)


# Connections

state = 'nz_chc'

passw = open('pass.txt', 'r').read().strip('\n')

host = '132.181.102.2'

port = '5001'

db_name = 'access_nz_chc'

engine = create_engine('postgresql+psycopg2://postgres:' + passw + '@' + host + '/' + db_name + '?port=' + port)

connect_string = "host=" + host + " dbname=" + db_name + " user=postgres password='"+ passw + "' port=" + port

osrm_url = 'http://localhost:6001'

con = psycopg2.connect(connect_string)

cursor = con.cursor()



def edit_raw():





    file = ['/homedirs/dak55/resilience_equity/data/census/i_18.csv', '/homedirs/dak55/resilience_equity/data/census/h_18.csv']

    #import csv

    i_1 = pd.read_csv(file[0], encoding = "ISO-8859-1")

    house = pd.read_csv(file[1], encoding = "ISO-8859-1")



        #init df:

    df = pd.DataFrame(columns = ['gid', 'population', 'male_pop', 'female_pop', 'median_age', 'pop_euro', 'pop_maori', 'pop_pacific', 'pop_asian', 'pop_melaa'])#, 'median_house_income'])

    #Add gid col in census df

    i_1['gid'] = None

        #Using a progressbar, strip the mb code and add just the digit code to col gid

    with tqdm(total = len(i_1)) as pbar:
        for i in range(len(i_1)):
            if type(i_1.Area_Code.iloc[i]) == int:
                i_1['gid'].iloc[i] = int(i_1.Area_Code.iloc[i])
                pbar.update()



        #populate columns

    df['gid'] = i_1['gid']

    df['population'] = i_1['Census_2018_CURP']

    df['male_pop'] = i_1['Census_2018_Sex_1_Male_CURP']

    df['female_pop'] = i_1['Census_2018_Sex_2_Female_CURP']

    df['median_age'] = i_1['2018_Census_Age..single_year_of_age_Median_CURP']

    df['pop_euro'] = i_1['Census_2018_Ethnicity..grouped_level_1_1_European_CURP']

    df['pop_maori'] = i_1['Census_2018_Ethnicity..grouped_level_1_2_MÄ\x81ori_CURP']

    df['pop_pacific'] = i_1['Census_2018_Ethnicity..grouped_level_1_3_Pacific.Peoples_CURP']

    df['pop_asian'] = i_1['Census_2018_Ethnicity..grouped_level_1_4_Asian_CURP']

    df['pop_melaa'] = i_1['Census_2018_Ethnicity..grouped_level_1_5_Middle.Eastern.Latin.American.African_CURP']

    #df['median_house_income'] = house['2006_Census_total_household_income_(grouped)(2)(3)(4)_for_households_in_occupied_private_dwellings_Median_household_income_($)(18)(23)']



    df.to_sql('census_18', engine)

    # commit

    con.commit()







def add_dem():

    '''

    Combines nearest dist and demographic data before uploading to postgresql

    '''

    #Pull datatables

    df_near = pd.read_sql('SELECT * FROM nearest_dist_18', con)

    df_cen = pd.read_sql('SELECT * FROM census_18', con)



    df_near['id_orig_1'] = df_near.id_orig

    df_cen['gid_1'] = df_cen.gid



    #Set index

    df_near = df_near.set_index('id_orig')

    df_cen = df_cen.set_index('gid')



    col_names = ['population', 'male_pop', 'female_pop', 'median_age', 'pop_euro', 'pop_maori', 'pop_pacific', 'pop_asian', 'pop_melaa']#, 'median_house_income']

    for name in col_names:

        df_near[name] = None





    with tqdm(total = len(df_near)) as pbar:

        for id in df_near.id_orig_1:

            if (df_cen.index==float(id)).any() == True:

                df_near['population'].loc[id] = df_cen.population.loc[float(id)]

                df_near['male_pop'].loc[id] = df_cen.male_pop.loc[float(id)]

                df_near['female_pop'].loc[id] = df_cen.female_pop.loc[float(id)]

                df_near['median_age'].loc[id] = df_cen.median_age.loc[float(id)]

                df_near['pop_euro'].loc[id] = df_cen.pop_euro.loc[float(id)]

                df_near['pop_maori'].loc[id] = df_cen.pop_maori.loc[float(id)]

                df_near['pop_pacific'].loc[id] = df_cen.pop_pacific.loc[float(id)]

                df_near['pop_asian'].loc[id] = df_cen.pop_asian.loc[float(id)]

                df_near['pop_melaa'].loc[id] = df_cen.pop_melaa.loc[float(id)]

                #df_near['median_house_income'].loc[id] = df_cen.median_house_income.loc[float(id)]

            pbar.update()



    df_near.to_sql('demo_18', engine)

    con.commit()



edit_raw()
