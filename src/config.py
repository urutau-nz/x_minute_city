'''
Imports functions and variables that are common throughout the project
'''

# functions - data analysis
import numpy as np
import pandas as pd
import itertools
# functions - geospatial
import geopandas as gpd
# functions - data management
import pickle as pk
import psycopg2
from sqlalchemy.engine import create_engine
# functions - coding
import code
import os
from datetime import datetime, timedelta
import time
from tqdm import tqdm
#plotting
from scipy.integrate import simps
import matplotlib.pyplot as plt
import random
import seaborn as sns
# logging
import logging
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

def cfg_init(state):
    # SQL connection
    db = dict()
    db['passw'] = open('pass.txt', 'r').read().strip('\n')
    db['host'] = '132.181.102.2'
    db['port'] = '5001'
    # city information
    context = dict()
    if state == 'nz_chc':
        db['name'] = 'access_nz_chc'
        context['city_code'] = 'chc'
        context['city'] = 'Christchurch'
        context['state'] = 'new-zealand'
        # url to the osrm routing machine
        context['port'] = '6001'
        context['services'] = ['supermarket', 'police_station', 'hospital', 'fire_station','medical_clinic']
    elif state == 'nz_ham':
        db['name'] = 'access_nz_ham'
        context['city_code'] = 'ham'
        context['city'] = 'Hamilton'
        context['state'] = 'new-zealand'
        # url to the osrm routing machine
        context['port'] = '6001'
        context['services'] = ['supermarket', 'police_station', 'hospital', 'fire_station','library']
    elif state == 'nz':
        db['name'] = 'access_nz'
        context['state'] = 'new-zealand'
        # url to the osrm routing machine
        context['port'] = '6001'


    context['osrm_url'] = 'http://localhost:' + context['port']
    # connect to database
    db['engine'] = create_engine('postgresql+psycopg2://postgres:' + db['passw'] + '@' + db['host'] + '/' + db['name'] + '?port=' + db['port'])
    db['address'] = "host=" + db['host'] + " dbname=" + db['name'] + " user=postgres password='"+ db['passw'] + "' port=" + db['port']
    db['con'] = psycopg2.connect(db['address'])
    return(db, context)
