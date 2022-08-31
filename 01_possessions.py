#%%
from utils import *
import pandas as pd

# dictionary of year to url
dict_worldtour = {
    2022: 'https://fiba3x3cdn.blob.core.windows.net/documents/Statistics/2022/WorldTour/FIBA_3x3_WT_Tour_Stats_After_005_Events.xlsx', 
    2021: 'https://fiba3x3cdn.blob.core.windows.net/documents/Statistics/2021/WorldTour/FIBA_3x3_WT_Tour_Stats_After_008_Events.xlsx',
    2020: 'https://fiba3x3cdn.blob.core.windows.net/documents/Statistics/2020/WorldTour/FIBA3x3_WT2020_Tour_Statistics_Post-Final.xlsx',
    2019: 'https://fiba3x3cdn.blob.core.windows.net/documents/Statistics/2019/WorldTour/FIBA_3x3_WT_Tour_Stats_2019_update04-12-2020.xlsx',
    2018: 'https://fiba3x3cdn.blob.core.windows.net/documents/Statistics/2018/WorldTour/Tour_Team_Statistics.xlsx',
    1520: 'https://fiba3x3cdn.blob.core.windows.net/documents/Statistics/2020/WorldTour/FIBA3x3%20_WT_Tour_Stats_2015-2020.xlsx' # 2015-2020 world tour stats
} 

# no challenger stats before 2019
dict_procircuit = {
    2022: 'https://fiba3x3cdn.blob.core.windows.net/documents/Statistics/2022/ProCircuitMen/FIBA_3x3_Pro_Circuit_Stats_After_016_Events.xlsx',
    2021: 'https://fiba3x3cdn.blob.core.windows.net/documents/Statistics/2021/ProCircuitMen/FIBA_3x3_Pro_Circuit_Stats_After_014_Events.xlsx',
    2020: 'https://fiba3x3cdn.blob.core.windows.net/documents/Statistics/2020/WorldTour/FIBA3x3_WT2020_Tour_Statistics_Post-Final.xlsx', # only WT in 2020
    2019: 'https://fiba3x3cdn.blob.core.windows.net/documents/Statistics/2019/WorldTour/FIBA_3x3_Pro_Circuit_Stats_2019_update04-12-2020.xlsx'
}

dict_womenseries = {
    2022:'https://fiba3x3cdn.blob.core.windows.net/documents/Statistics/2022/WomensSeries/FIBA_3x3_WS_Tour_Stats_After_010_Events.xlsx',
    2021:'https://fiba3x3cdn.blob.core.windows.net/documents/Statistics/2021/WomensSeries/FIBA_3x3_WS_Tour_Stats.xlsx',
    2019:'https://fiba3x3cdn.blob.core.windows.net/documents/Statistics/2019/WomensSeries/FIBA3x3_Womens_Series_2019_Team_and_Player_Stats_Season_2019.xlsx'
}

#%%
list_season_stats = []
for season in [2019]:
    dict_df = pd.read_excel(dict_procircuit[season], None)
    if season == 2019:
        df_team = dict_df['Team']
    else:
        df_team = dict_df['Teams']
    list_season_stats.append(season_stats(df_team, season))
