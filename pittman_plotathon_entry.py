#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  9 15:50:04 2021
For DataTas Plot-A-Thon!
@author: Nic Pittman
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#from matplotlib.colors import SymLogNorm

# Load and Data cleanup roughly copied from the R version.
peaks=pd.read_csv('data/peaks.csv')
expeds=pd.read_csv('data/expeditions.csv')
members=pd.read_csv('data/members.csv')

# COMBINED DF
combined_df=pd.merge(members,peaks,how='right',on='peak_id',suffixes=('', '_x'))
combined_df=pd.merge(combined_df,expeds,how='right',on='expedition_id',suffixes=('', '_y'))
members_all_fields=combined_df.dropna(axis=0,thresh=20)

print('Variables\n---------')
print(list(combined_df))




# %% Algorithm to find the countries of citizenship that climb each mountain. 
# There may be a more elegant pandas join solution to do this? But i dont know it. 
# But lets try brute force method!!!!
# Oh oops this definitely turned into a monster. Better solution to saving the output in Xarray? 

peaks_by_climbers=members.groupby(by='peak_name').groups
citizenship_per_mountain_holder=[] # Holder list to concat our pandas series
age_per_mountain_holder=[]
success_per_mountain_holder=[]
died_per_mountain_holder=[]


# Numerous solutions for this. Turned into something horrible. 
for peak_id_iterable in peaks_by_climbers.keys():
    # print(peak_id_iterable)
    climber_indexes=peaks_by_climbers[peak_id_iterable]
    members_who_climbed_this_peak=members.iloc[peaks_by_climbers[peak_id_iterable]]
    unique_expeditions=members_who_climbed_this_peak.expedition_id.unique()
    
    number_of_country_climbs=members_who_climbed_this_peak.citizenship.value_counts()
    number_of_country_climbs.name=peak_id_iterable
    
    citizen_group=members_who_climbed_this_peak.groupby('citizenship').mean()
    
       
    citizenship_per_mountain_holder.append(pd.DataFrame(number_of_country_climbs).T)

    age_df=pd.Series(citizen_group.age,name=peak_id_iterable).T
    age_df.name=peak_id_iterable
    age_per_mountain_holder.append(age_df)
        
    success_df=pd.Series(citizen_group.success,name=peak_id_iterable).T
    success_df.index.name=peak_id_iterable
    success_per_mountain_holder.append(success_df)
    
    died_df=pd.Series(citizen_group.died,name=peak_id_iterable).T
    died_df.index.name=peak_id_iterable
    died_per_mountain_holder.append(died_df)

citizens_per_mountain=pd.concat(citizenship_per_mountain_holder,sort=True).T
age_per_mountain=pd.concat(age_per_mountain_holder,sort=True,axis=1).T
success_per_mountain=pd.concat(success_per_mountain_holder,sort=True,axis=1).T
died_per_mountain=pd.concat(died_per_mountain_holder,sort=True,axis=1).T


# %% PLOT
def himalayanPlotter(df,
            subplot,
            title,
            log=False):

    ax = plt.subplot(subplot)
    
    # if log==True:
    #     norm = SymLogNorm(10,vmin=0,vmax=6000)
          
    #     heatmap = ax.pcolormesh(df, cmap=plt.cm.Reds,norm=norm)
    # else:
    heatmap = ax.pcolormesh(df, cmap=plt.cm.Reds)
    plt.colorbar(heatmap,ax=ax)#,extend='max')   
    ax.set_yticks(np.arange(df.shape[0]) + 0.5, minor=False)
    ax.set_xticks(np.arange(df.shape[1]) + 0.5, minor=False)
    ax.set_xticklabels(df.columns, minor=False,rotation=270)
    ax.set_yticklabels(df.index, minor=False)
    
    plt.title(title)
    # %%
    
plt.figure(figsize=(18,22))
himalayanPlotter(citizens_per_mountain.T.dropna(thresh=40,axis=1).dropna(thresh=12,axis=0),
        subplot=221,
        #log=True,
        title='The number of climbers from the top 25 nationalities for 25 mountains')
himalayanPlotter(died_per_mountain.dropna(thresh=40,axis=1).dropna(thresh=10,axis=0).astype(float),
        subplot=222,
        title='Percent of Deaths from the top nationalities and mountains')
himalayanPlotter(success_per_mountain.dropna(thresh=40,axis=1).dropna(thresh=10,axis=0).astype(float),
        subplot=223,
        title='Percent of success from the top nationalities and mountains')
himalayanPlotter(age_per_mountain.dropna(thresh=40,axis=1).dropna(thresh=10,axis=0).astype(float),
        subplot=224,
        title='Average age of the top nationalities and mountains climbed')

plt.tight_layout()
plt.savefig('PittmanHimalyanEntry.png',format='png',dpi=300)
plt.show()



# # %% Old drafting  Lets find What happens at each of these tourist agencies
# Not sure why I couldnt get the whole thing output by the regex. Regex out the first two words
# Maybe something to do with `str.extract`.
# This allows sorting because there are many company subsidiaries that make the groupby a challenge.
# Actually redundant now but left because interesting solution.
# agency_word1=members_all_fields.trekking_agency.str.extract('^(\S+\s){1}')
# agency_word2=members_all_fields.trekking_agency.str.extract('^(\S+\s){2}').replace(np.nan,'')
# members_all_fields['TrekkingAgencyNameShort']=agency_word1+agency_word2

# members_by_agency=members_all_fields.groupby('TrekkingAgencyNameShort')
# members_by_peak=members_all_fields.groupby('peak_name')

# for agency_iterable in members_by_agency.groups:
#     agency_indexes=members_by_agency.groups[agency_iterable]
    
#     members_who_went_with_agency=members_all_fields.iloc[agency_indexes]

#     members_who_climbed_this_peak=members_by_agency.get_group(agency_iterable)
#     unique_expeditions=members_who_climbed_this_peak.expedition_id.unique()
    
#     number_of_country_climbs=members_who_climbed_this_peak.citizenship.value_counts()
    
#     # Clean up so we can work it later