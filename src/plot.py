import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

# import the durations
duration = pd.read_csv('data/duration.csv')

population = duration.drop_duplicates(subset=['id_orig']).groupby('city').sum()['population']

duration.loc[duration.city=='christchurch','population'] = duration.loc[duration.city=='christchurch','population']/population['christchurch']*100
duration.loc[duration.city=='hamilton','population'] = duration.loc[duration.city=='hamilton','population']/population['hamilton']*100

# calculate what percentage of people live within some cut off time
duration_10 = duration[duration.duration <= 10 * 60].groupby(['city','dest_type','mode']).sum()

duration_15 = duration[duration.duration <= 15 * 60].groupby(['city','dest_type','mode']).sum()

city = 'christchurch'


dur10chc = duration_15.loc[city]
dur10chc = dur10chc.reset_index()
dur10chc = dur10chc[dur10chc.dest_type.isin(['downtown','supermarket','medical_clinic','primary_school'])][['dest_type','mode','population']]
dur10chc = dur10chc[dur10chc['mode'].isin(['walking','cycling'])]
dur10chc = dur10chc.set_index('dest_type')
dur10chc = dur10chc.pivot(columns='mode',values='population')
# plt.figure(figsize=(15,5))
ax = dur10chc.plot.bar(rot=0,figsize=(6.25,2), yticks=[0,50,100])
for p in ax.patches:
    ax.annotate(np.round(p.get_height(),decimals=1), (p.get_x()+p.get_width()/2., p.get_height()), ha='center', va='center', xytext=(0, 10), textcoords='offset points')

# plot
dur10chc = duration_10.loc[city]
dur10chc = dur10chc.reset_index()
dur10chc = dur10chc[dur10chc.dest_type.isin(['downtown','supermarket','medical_clinic','primary_school'])][['dest_type','mode','population']]
dur10chc = dur10chc[dur10chc['mode'].isin(['walking','cycling'])]
dur10chc = dur10chc.set_index('dest_type')
dur10chc = dur10chc.pivot(columns='mode',values='population')
# plt.figure(figsize=(15,5))
ax = dur10chc.plot.bar(rot=0,figsize=(6.25,2), yticks=[0,50,100], edgecolor='black', color='none', ax=ax, legend=False, linewidth=0.5)
# for p in ax.patches:
#     ax.annotate(np.round(p.get_height(),decimals=1), (p.get_x()+p.get_width()/2., p.get_height()), ha='center', va='center', xytext=(0, 10), textcoords='offset points')

plt.savefig('fig/{}_access.pdf'.format(city), dpi=500, format='pdf', transparent=True)#, bbox_inches='tight')

# fig1, ax1 = plt.subplots(figsize=(10,4))
# df['A'].plot(ax=ax1)
# fig1.savefig("plot1.png")
