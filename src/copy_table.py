'''
copies a table from one database to another
'''

from config import *
from_state = input("State transferring from: ")
table_name = input("table name: ")
db_from, context_from = cfg_init(from_state)
db_to, context_to = cfg_init(from_state)
to_state = input("State transferring too: ")

sql = "SELECT * FROM {}".format(table_name)
df = pd.read_sql(sql, db_from['con'])
df.to_sql(table_name, db_to['engine'], if_exists='replace')
