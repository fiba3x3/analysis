# This file contains utility functions
from typing import List
from scipy import stats
import numpy as np
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

# no challenger stats before 2019, no challenger in 2020
dict_procircuit = {
    2022: 'https://fiba3x3cdn.blob.core.windows.net/documents/Statistics/2022/ProCircuitMen/FIBA_3x3_Pro_Circuit_Stats_After_016_Events.xlsx',
    2021: 'https://fiba3x3cdn.blob.core.windows.net/documents/Statistics/2021/ProCircuitMen/FIBA_3x3_Pro_Circuit_Stats_After_014_Events.xlsx',
    2019: 'https://fiba3x3cdn.blob.core.windows.net/documents/Statistics/2019/WorldTour/FIBA_3x3_Pro_Circuit_Stats_2019_update04-12-2020.xlsx'
}

dict_womenseries = {
    2022:'https://fiba3x3cdn.blob.core.windows.net/documents/Statistics/2022/WomensSeries/FIBA_3x3_WS_Tour_Stats_After_010_Events.xlsx',
    2021:'https://fiba3x3cdn.blob.core.windows.net/documents/Statistics/2021/WomensSeries/FIBA_3x3_WS_Tour_Stats.xlsx',
    2019:'https://fiba3x3cdn.blob.core.windows.net/documents/Statistics/2019/WomensSeries/FIBA3x3_Womens_Series_2019_Team_and_Player_Stats_Season_2019.xlsx'
}

def advanced_stats(df_teams: pd.DataFrame, season:int = 0) -> pd.DataFrame:
    """
    Compute advanced stats for teams 
    
    Parameters
    ----------
    df_teams: pd.DataFrame
        dataframe with team stats from FIBA 3x3 stats website 
        e.g. https://fiba3x3cdn.blob.core.windows.net/documents/Statistics/2022/WomensSeries/FIBA_3x3_WS_Tour_Stats_After_009_Events.xlsx

    Returns
    -------
    df_teams: pd.DataFrame
        dataframe with more columns
    """
    # rename certain columns that changed after 2020 season 
    df_teams.rename(columns={"PTA1":"1PTA", 
                            "PT1" : "1PTM",
                            "PTA2":"2PTA",
                            "PT2":"2PTM",
                            "FT":"FTM",
                            "PT1Percentage":"1PT%",
                            "PT2Percentage" : "2PT%",
                            "FTPercentage" : "FT%",
                            "FT-ES" : "FTES"
                        }, inplace=True
                    )
    
    # additional count stats
    df_teams['POS'] = df_teams.eval('GP * POSPG') # FIBA version over counting real number of possessions
    df_teams['FGA'] = (df_teams['2PTA'] + df_teams['1PTA']) # total field goals attempt
    df_teams['FGM'] = (df_teams['2PTM'] + df_teams['1PTM']) # total field goals made
    
    df_teams['eFG'] = (df_teams['1PTM'] + 2*df_teams['2PTM'])/ df_teams['FGA'] # eFG for 3x3  
    df_teams['OREB%'] = df_teams.eval('OREB / (FGA-FGM + (FTA-FTM)*(1-FTES/FTA))') # need to account for technical free throws, cannot compute DREB%
    df_teams['WBLGP'] = df_teams.eval('WBL / GP') # FTA per fouled

    # KAS 
    df_teams['KASTO'] = df_teams.eval('KAS / TO')
    df_teams['KASFGM'] = df_teams.eval('KAS / FGM') # key assist to made shot ratio
    
    # points distribution
    df_teams['1PTMPTS'] = df_teams.eval(' `1PTM` / PTS')
    df_teams['2PTMPTS'] = df_teams.eval(' `2PTM` / PTS')
    df_teams['FTMPTS'] = df_teams.eval(' FTM / PTS')
    df_teams['DRV1PTM'] = df_teams.eval(' DRV / `1PTM`')
    
    # per possession
    df_teams['TOPOS'] = df_teams.eval('TO / POS')
    df_teams['1PTAPOS'] = df_teams['1PTA'] / df_teams.POS
    df_teams['2PTAPOS'] = df_teams['2PTA'] / df_teams.POS
    df_teams['FTAPOS'] = df_teams.eval('FTA / POS')
    df_teams['PPP'] = df_teams.eval("PTS / POS")
    df_teams['TFAPOS'] = df_teams.eval('TFA / POS') # fouled per possession
    df_teams['TFPOS'] = df_teams.eval('TF / POS') # foul per possession
    df_teams['TFAPOS'] = df_teams.eval('TFA / POS') # fouled per possession

    # foul
    df_teams['TOTF'] = df_teams.eval('TO / TF') # turnover to foul ratio
    df_teams['BSTF'] = df_teams.eval('BS / TF') # blocked shots to foul ratio
    
    df_teams['TOTFA'] = df_teams.eval('TO / TFA') # turnover to fouled ratio
    df_teams['TFTFA'] = df_teams.eval('TF / TFA') # foul to fouled ratio
    df_teams['FTATFA'] = df_teams.eval('FTA / TFA') # FTA per fouled
    df_teams['FTESTFA'] = df_teams.eval('FTES / TFA') # extra free throws to fouled ratio
    df_teams['FTMTFA'] = df_teams.eval('FTM / TFA') # free throw made to fouled ratio
    
    df_teams['FTESFTA'] = df_teams.eval('FTES / FTA') # extra FT per FTA
    df_teams['season'] = season
    
    return df_teams

def season_stats(df_teams: pd.DataFrame, season:int = 0)-> pd.DataFrame:
    """
    Compute season advanced stats
    """
    df_teams.rename(columns={"PTA1":"1PTA", 
                        "PT1" : "1PTM",
                        "PTA2":"2PTA",
                        "PT2":"2PTM",
                        "FT":"FTM",
                        "PT1Percentage":"1PT%",
                        "PT2Percentage" : "2PT%",
                        "FTPercentage" : "FT%",
                        "FT-ES" : "FTES"
                    }, inplace=True
    )
    list_tuple_season_stat = [] # list to store tuples of stat name and stat

    # count stats
    df_teams['POS'] = df_teams.eval('GP * POSPG') # FIBA over counting real number of possessions
    df_teams['FGA'] = df_teams['2PTA'] + df_teams['1PTA'] # total field goals attempt
    df_teams['FGM'] = df_teams['2PTM'] + df_teams['1PTM']# total field goals made
    
    list_tuple_season_stat.append( ('GP', df_teams.eval('GP.sum()')/2) )
    list_tuple_season_stat.append( ('POS_FIBA', df_teams.eval('POS.sum()')) )
    list_tuple_season_stat.append( ('POS_ESTIMATE', df_teams['1PTM'].sum() + df_teams['2PTM'].sum() + df_teams.eval('TO.sum() + DREB.sum() + (1-FTES.sum()/FTA.sum())*FTM.sum()') ) )
    
    # box score stats
    list_tuple_season_stat.append( ('POSPG', df_teams.eval('POS.sum() / GP.sum()')) )
    list_tuple_season_stat.append( ('1PT%', df_teams['1PTM'].sum() / df_teams['1PTA'].sum()) )
    list_tuple_season_stat.append( ('2PT%', df_teams['2PTM'].sum() / df_teams['2PTA'].sum()) )    
    list_tuple_season_stat.append( ('FT%', df_teams.eval('FTM.sum() / FTA.sum()')) )

    # rebounding stats
    list_tuple_season_stat.append( ('OREB%', df_teams.eval('OREB.sum() / REB.sum()')) )
    list_tuple_season_stat.append( ('DREB%', df_teams.eval('DREB.sum() / REB.sum()')) )
    list_tuple_season_stat.append( ('FTOREB%', df_teams.eval('( OREB.sum() - (FGA.sum() - FGM.sum()) * OREB.sum() / REB.sum() ) / ( (FTA.sum()-FTM.sum())*(1 - FTES.sum()/FTA.sum()) )')) ) # need to account for technical free throws, denominator should be smaller
    # list_tuple_season_stat.append( ('FTDREB%', df_teams.eval('( DREB.sum() - (FGA.sum() - FGM.sum()) * DREB.sum() / REB.sum() ) / ( (FTA.sum()-FTM.sum())*(1 - FTES.sum()/FTA.sum()) )')) ) # need to account for technical free throws, denominator should be smaller
    
    # points distribution
    list_tuple_season_stat.append( ('1PTMPTS',  df_teams['1PTM'].sum() / df_teams['PTS'].sum()) )
    list_tuple_season_stat.append( ('2PTMPTS', df_teams['2PTM'].sum() / df_teams['PTS'].sum()) )
    list_tuple_season_stat.append( ('FTMPTS', df_teams.eval('FTM.sum() / PTS.sum()')) )
    list_tuple_season_stat.append( ('DRV1PTM', df_teams.eval('DRV.sum()') / df_teams['1PTM'].sum()) )

    # per possession stats
    list_tuple_season_stat.append( ('TOPOS', df_teams.eval('TO.sum() / POS.sum()')) ) # turnovers
    list_tuple_season_stat.append( ('1PTAPOS',  df_teams['1PTA'].sum() / df_teams['POS'].sum()) )
    list_tuple_season_stat.append( ('2PTAPOS',  df_teams['2PTA'].sum() / df_teams['POS'].sum()) )
    list_tuple_season_stat.append( ('TFAPOS', df_teams.eval('TFA.sum() / POS.sum()')) ) # fouled per possession
    list_tuple_season_stat.append( ('FTAPOS', df_teams.eval('FTA.sum() / POS.sum()')) ) # FTA per possession 
    list_tuple_season_stat.append( ('PPP', df_teams.eval('PTS.sum() / POS.sum()')) )
    list_tuple_season_stat.append( ('TFAPOS', df_teams.eval('TFA.sum() / POS.sum()')) ) # fouled per possession
    list_tuple_season_stat.append( ('TFPOS', df_teams.eval('TF.sum() / POS.sum()')) ) # fouls per possession
    
    # foul stats
    list_tuple_season_stat.append( ('TOTF', df_teams.eval('TO.sum() / TF.sum()') ) ) # turnover to foul ratio
    list_tuple_season_stat.append( ('BSTF', df_teams.eval('BS.sum() / TF.sum()')) ) # blocked shots to foul ratio
    
    list_tuple_season_stat.append( ('TOTFA', df_teams.eval('TO.sum() / TFA.sum()') ) ) # turnover to fouled ratio
    list_tuple_season_stat.append( ('TFTFA', df_teams.eval('TF.sum() / TFA.sum()') ) ) # foul to fouled ratio
    list_tuple_season_stat.append( ('FTATFA', df_teams.eval('FTA.sum() / TFA.sum()') ) ) # FTA to fouled ratio
    list_tuple_season_stat.append( ('FTESTFA', df_teams.eval('FTES.sum() / TFA.sum()') ) ) # extra FTA to fouled ratio    
    list_tuple_season_stat.append( ('FTMTFA', df_teams.eval('FTM.sum() / TFA.sum()') ) ) # free throw made to fouled ratio    
    
    list_tuple_season_stat.append( ('FTESFTA', df_teams.eval('FTES.sum() / FTA.sum()') ) ) # extra FTA per FTA
    
    # key assist
    list_tuple_season_stat.append( ('KASTO', df_teams.eval('KAS.sum() / TO.sum()')) )
    list_tuple_season_stat.append( ('KASFGM', df_teams.eval('KAS.sum() / FGM.sum()')) )
    
    df = pd.DataFrame({x[0]:x[1:] for x in list_tuple_season_stat})
    df['season'] = season
    return df

def player_stats(df: pd.DataFrame, season:int = 0)-> pd.DataFrame:
    
    """
    Compute season advanced stats
    """
    
    # points distribution
    df['1PTMPTS'] = df.eval('1PTM / PTS')
    df['2PTMPTS'] = df.eval('2PTM / PTS')
    df['FTMPTS'] = df.eval('FTM / PTS')
    df['DRV1PTM'] = df.eval('DRV / 1PTM')
    
    return df

def make_df_multiple_season_stat(dict_:dict, seasons:List[int], tour_type:str) -> pd.DataFrame:
    """
    Helper function to make dataframe for multiple seasons' stats
    """
    list_season_stats = []
    for season in seasons:
        dict_df = pd.read_excel(dict_[season], None)
        if season == 2019 and tour_type in['Pro Circuit', 'World Tour']:
            df_team = dict_df['Team']
        elif season == 2019:
            df_team = dict_df['WS 2019 - Teams']
        else:
            df_team = dict_df['Teams']
        list_season_stats.append(season_stats(df_team, season))
        
    df = pd.concat(list_season_stats)
    df['type'] = tour_type
    return df

def make_df_multiple_season_team_advanced_stat(dict_:dict, seasons:List[int], tour_type:str) -> pd.DataFrame:
    """
    Helper function to make dataframe for multiple seasons' team advanced stats
    """
    list_season_stats = []
    for season in seasons:
        dict_df = pd.read_excel(dict_[season], None)
        if season == 2019 and tour_type in['Pro Circuit', 'World Tour']:
            df_team = dict_df['Team']
        elif season == 2019:
            df_team = dict_df['WS 2019 - Teams']
        else:
            df_team = dict_df['Teams']
        list_season_stats.append(advanced_stats(df_team, season))
        
    df = pd.concat(list_season_stats)
    df['type'] = tour_type
    return df

def corr_annotation(x : np.array, y : np.array) -> str:
    """
    Compute pearson correlation coefficient and p-value
    """
    pearsonr = stats.pearsonr(x, y)
    return 'pearson r = {:.2f} (p = {:.3f})'.format(pearsonr[0], pearsonr[1])