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

def advanced_stats(df: pd.DataFrame, season:int = 0) -> pd.DataFrame:
    """
    Compute advanced stats for teams 
    
    Parameters
    ----------
    df: pd.DataFrame
        dataframe with team stats from FIBA 3x3 stats website 
        e.g. https://fiba3x3cdn.blob.core.windows.net/documents/Statistics/2022/WomensSeries/FIBA_3x3_WS_Tour_Stats_After_009_Events.xlsx

    Returns
    -------
    df: pd.DataFrame
        dataframe with more columns
    """
    # rename certain columns that changed after 2020 season 
    df.rename(columns={"PTA1":"1PTA", 
                            "PT1" : "1PTM",
                            "PTA2":"2PTA",
                            "PT2":"2PTM",
                            "FT":"FTM",
                            "PT1Percentage":"1PT%",
                            "PT2Percentage" : "2PT%",
                            "FTPercentage" : "FT%",
                            "FT-ES" : "FTES",
                        }, inplace=True
                    )
    col_to_drop = [x for x in ["PTA2_FGA", "2PTA/FGA", "PTA2POS"] if x in df.columns]
    df.drop(columns=col_to_drop, inplace=True)
    
    # estimated total possession for season
    POS_estimate = df['1PTM'].sum() + df['2PTM'].sum() + df.eval('TO.sum() + DREB.sum() + (1-FTES.sum()/FTA.sum())*FTM.sum()') 

    # additional count stats
    df.eval('POS = GP * POSPG', inplace=True) # FIBA version over counting real number of possessions
    POS_FIBA = df['POS'].sum()
    df['POS'] = df['POS'] * POS_estimate/POS_FIBA # use a correction factor as opponent DREB is not available for computing team possessions
    df['POSPG'] = df.eval('POS / GP') # recompute POSPG
    df['FGA'] = (df['2PTA'] + df['1PTA']) # total field goals attempt
    df['FGM'] = (df['2PTM'] + df['1PTM']) # total field goals made
    
    df['eFG'] = (df['1PTM'] + 2*df['2PTM'])/ df['FGA'] # eFG for 3x3  
    df['OREB%'] = df.eval('OREB / (FGA-FGM + (FTA-FTM)*(1-FTES/FTA))') # need to account for technical free throws, cannot compute DREB%
    df['WBLPG'] = df.eval('WBL / GP') 

    # KAS 
    df['KASTO'] = df.eval('KAS / TO')
    df['KASFGM'] = df.eval('KAS / FGM') # key assist to made shot ratio
    
    # points distribution
    df['1PTMPTS'] = df.eval(' `1PTM` / PTS')
    df['2PTMPTS'] = df.eval(' 2 * `2PTM` / PTS')
    df['FTMPTS'] = df.eval(' FTM / PTS')
    df['DRV1PTM'] = df.eval(' DRV / `1PTM`')
    df['2PTAFGA'] = df.eval('`2PTA` / FGA') # 2 point attempts per FGA
    
    # per possession
    df['TOPOS'] = df.eval('TO / POS')
    df['1PTAPOS'] = df['1PTA'] / df.POS
    df['2PTAPOS'] = df['2PTA'] / df.POS
    df['FGAPOS'] = df['FGA'] / df.POS
    df['PPP'] = df.eval("PTS / POS")
    df['TFAPOS'] = df.eval('TFA / POS') # fouled per possession
    df['FTAPOS'] = df.eval('FTA / POS')
    df['TFPOS'] = df.eval('TF / POS') # foul per possession
    df['FTTPOS'] = df.eval('(FTA-FTES) / POS') # trip to free throw per possession

    # foul
    df['TOTF'] = df.eval('TO / TF') # turnover to foul ratio
    df['BSTF'] = df.eval('BS / TF') # blocked shots to foul ratio
    
    df['TOTFA'] = df.eval('TO / TFA') # turnover to fouled ratio
    df['TFTFA'] = df.eval('TF / TFA') # foul to fouled ratio
    df['FTATFA'] = df.eval('FTA / TFA') # FTA per fouled
    df['FTESTFA'] = df.eval('FTES / TFA') # extra free throws to fouled ratio
    df['FTMTFA'] = df.eval('FTM / TFA') # free throw made to fouled ratio
    df['FTTTFA'] = df.eval('(FTA-FTES) / TFA') # trip to free throw to fouled ratio
    df['FTESFTA'] = df.eval('FTES / FTA') # extra FT per FTA
    df['season'] = season
    
    return df

def season_stats(df: pd.DataFrame, season:int = 0)-> pd.DataFrame:
    """
    Compute season advanced stats
    """
    df.rename(columns={"PTA1":"1PTA", 
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
    col_to_drop = [x for x in ["PTA2_FGA", "2PTA/FGA", "PTA2POS"] if x in df.columns]
    df.drop(columns=col_to_drop, inplace=True) # replace with alternatve count of 2PTA per possession

    list_tuple_season_stat = [] # list to store tuples of stat name and stat

    # count stats
    df['POS'] = df.eval('GP * POSPG') # FIBA over counting real number of possessions
    POS_FIBA = df['POS'].sum()
    POS_estimate = df['1PTM'].sum() + df['2PTM'].sum() + df.eval('TO.sum() + DREB.sum() + (1-FTES.sum()/FTA.sum())*FTM.sum()') 
    df['POS'] = df['POS'] * POS_estimate/POS_FIBA # use a correction factor as opponent DREB is not available for computing team possessions
    df['FGA'] = df['2PTA'] + df['1PTA'] # total field goals attempt
    df['FGM'] = df['2PTM'] + df['1PTM']# total field goals made
    
    list_tuple_season_stat.append( ('GP', df.eval('GP.sum()')/2) )
    list_tuple_season_stat.append( ('POS_FIBA', df.eval('POS.sum()')) )
    list_tuple_season_stat.append( ('POS_ESTIMATE', df['1PTM'].sum() + df['2PTM'].sum() + df.eval('TO.sum() + DREB.sum() + (1-FTES.sum()/FTA.sum())*FTM.sum()') ) )
    
    # box score stats
    list_tuple_season_stat.append( ('POSPG', df.eval('POS.sum() / GP.sum()')) ) # used alternative definition of possession
    list_tuple_season_stat.append( ('1PT%', df['1PTM'].sum() / df['1PTA'].sum()) )
    list_tuple_season_stat.append( ('2PT%', df['2PTM'].sum() / df['2PTA'].sum()) )    
    list_tuple_season_stat.append( ('FT%', df.eval('FTM.sum() / FTA.sum()')) )
    list_tuple_season_stat.append( ('eFG', (df['1PTM'].sum() + 2*df['2PTM'].sum())/ df['FGA'].sum() ) )
    list_tuple_season_stat.append( ('S-EFF', df['PTS'].sum() / (df['FTA'].sum() + df['FGA'].sum() ) ) )
    # list_tuple_season_stat.append( ('S-VAL', (df['PTS'].sum())**2 / (df['FTA'].sum() + df['FGA'].sum() ) ) )
    list_tuple_season_stat.append( ('WBLPG', df['WBL'].sum() / df['GP'].sum() ) )
    list_tuple_season_stat.append( ('PPG', df['PTS'].sum() / df['GP'].sum() ) )

    # rebounding stats
    list_tuple_season_stat.append( ('OREB%', df.eval('OREB.sum() / REB.sum()')) )
    list_tuple_season_stat.append( ('DREB%', df.eval('DREB.sum() / REB.sum()')) )
    list_tuple_season_stat.append( ('FTOREB%', df.eval('( OREB.sum() - (FGA.sum() - FGM.sum()) * OREB.sum() / REB.sum() ) / ( (FTA.sum()-FTM.sum())*(1 - FTES.sum()/FTA.sum()) )')) ) # need to account for technical free throws, denominator should be smaller
    # list_tuple_season_stat.append( ('FTDREB%', df.eval('( DREB.sum() - (FGA.sum() - FGM.sum()) * DREB.sum() / REB.sum() ) / ( (FTA.sum()-FTM.sum())*(1 - FTES.sum()/FTA.sum()) )')) ) # need to account for technical free throws, denominator should be smaller
    
    # points distribution
    list_tuple_season_stat.append( ('1PTMPTS',  df['1PTM'].sum() / df['PTS'].sum()) )
    list_tuple_season_stat.append( ('2PTMPTS', 2*df['2PTM'].sum() / df['PTS'].sum()) )
    list_tuple_season_stat.append( ('FTMPTS', df.eval('FTM.sum() / PTS.sum()')) )
    list_tuple_season_stat.append( ('DRV1PTM', df.eval('DRV.sum()') / df['1PTM'].sum()) )
    list_tuple_season_stat.append( ('2PTAFGA', df['2PTA'].sum() / df['FGA'].sum()) ) # 2 point attempts per FGA

    # per possession stats
    list_tuple_season_stat.append( ('TOPOS', df.eval('TO.sum() / POS.sum()')) ) # turnovers
    list_tuple_season_stat.append( ('1PTAPOS',  df['1PTA'].sum() / df['POS'].sum()) )
    list_tuple_season_stat.append( ('2PTAPOS',  df['2PTA'].sum() / df['POS'].sum()) )
    list_tuple_season_stat.append( ('FGAPOS', df.eval('FGA.sum() / POS.sum()')) ) # FGA per possession
    list_tuple_season_stat.append( ('PPP', df.eval('PTS.sum() / POS.sum()')) )
    list_tuple_season_stat.append( ('TFAPOS', df.eval('TFA.sum() / POS.sum()')) ) # fouled per possession
    list_tuple_season_stat.append( ('FTAPOS', df.eval('FTA.sum() / POS.sum()')) ) # FTA per possession 
    list_tuple_season_stat.append( ('TFAPOS', df.eval('TFA.sum() / POS.sum()')) ) # fouled per possession
    list_tuple_season_stat.append( ('TFPOS', df.eval('TF.sum() / POS.sum()')) ) # fouls per possession
    list_tuple_season_stat.append( ('FTTPOS', df.eval('(FTA.sum() - FTES.sum())/ POS.sum()') ) ) # trip to free throw per possession
    # chance per possession
    
    # foul stats
    list_tuple_season_stat.append( ('TOTF', df.eval('TO.sum() / TF.sum()') ) ) # turnover to foul ratio
    list_tuple_season_stat.append( ('BSTF', df.eval('BS.sum() / TF.sum()')) ) # blocked shots to foul ratio
    
    list_tuple_season_stat.append( ('TOTFA', df.eval('TO.sum() / TFA.sum()') ) ) # turnover to fouled ratio
    list_tuple_season_stat.append( ('TFTFA', df.eval('TF.sum() / TFA.sum()') ) ) # foul to fouled ratio
    list_tuple_season_stat.append( ('FTATFA', df.eval('FTA.sum() / TFA.sum()') ) ) # FTA to fouled ratio
    list_tuple_season_stat.append( ('FTESTFA', df.eval('FTES.sum() / TFA.sum()') ) ) # extra FTA to fouled ratio    
    list_tuple_season_stat.append( ('FTMTFA', df.eval('FTM.sum() / TFA.sum()') ) ) # free throw made to fouled ratio    
    list_tuple_season_stat.append( ('FTTTFA', df.eval('(FTA.sum() - FTES.sum())/ TFA.sum()') ) ) # free throw trips to fouled ratio
    list_tuple_season_stat.append( ('FTESFTA', df.eval('FTES.sum() / FTA.sum()') ) ) # extra FTA per FTA
    
    # key assist
    list_tuple_season_stat.append( ('KASTO', df.eval('KAS.sum() / TO.sum()')) )
    list_tuple_season_stat.append( ('KASFGM', df.eval('KAS.sum() / FGM.sum()')) )
    
    df = pd.DataFrame({x[0]:x[1:] for x in list_tuple_season_stat})
    df['season'] = season
    return df

def player_stats(df: pd.DataFrame, season:int = 0)-> pd.DataFrame:
    """
    Compute player advanced stats
    """
    # rename certain columns that changed after 2020 season 
    df.rename(columns={ "PTA1":"1PTA", 
                        "PT1" : "1PTM",
                        "PTA2":"2PTA",
                        "PT2":"2PTM",
                        "FT":"FTM",
                        "PTA1_TEAM":"1PTA_TEAM", 
                        "PT1_TEAM" : "1PTM_TEAM",
                        "PTA2_TEAM":"2PTA_TEAM",
                        "PT2_TEAM":"2PTM_TEAM",
                        "FT_TEAM":"FTM_TEAM",
                        "PT1Percentage":"1PT%",
                        "PT2Percentage" : "2PT%",
                        "FTPercentage" : "FT%",
                        "FT-ES" : "FTES",
                        }, inplace=True
                    )
    col_to_drop = [x for x in ["PTA2_FGA", "2PTA/FGA", "PTA2POS"] if x in df.columns]
    df.drop(columns=col_to_drop, inplace=True)
    
    # box score
    df['FGA'] = (df['2PTA'] + df['1PTA']) # total field goals attempt
    df['FGA_TEAM'] = (df['2PTA_TEAM'] + df['1PTA_TEAM']) # total field goals attempt
    df['FGM'] = (df['2PTM'] + df['1PTM']) # total field goals made
    df['FGM_TEAM'] = (df['2PTM_TEAM'] + df['1PTM_TEAM']) # total field goals made
    df['eFG'] = (df['1PTM'] + 2*df['2PTM'])/ df['FGA'] # eFG for 3x3  
    # df['OREB%'] = df.eval('OREB / (FGA-FGM + (FTA-FTM)*(1-FTES/FTA))') # need to account for technical free throws, cannot compute DREB%
    
    # team based 
    df['GP_TEAM%'] = df.eval('GP / GP_TEAM') # fraction of all games played
    df['PTS_TEAM%'] = df['PTS'] / df['PTS_TEAM']
    df['FGA_TEAM%'] = df['FGA'] / df['FGA_TEAM']
    df['FGM_TEAM%'] = df['FGM'] / df['FGM_TEAM']
    df['1PTM_TEAM%'] = df['1PTM'] / df['1PTM_TEAM']
    df['1PTA_TEAM%'] = df['1PTA'] / df['1PTA_TEAM']
    df['2PTM_TEAM%'] = df['2PTM'] / df['2PTM_TEAM']
    df['2PTA_TEAM%'] = df['2PTA'] / df['2PTA_TEAM']
    df['KAS_TEAM%'] = df['KAS'] / df['KAS_TEAM']
    df['TO_TEAM%'] = df['TO'] / df['TO_TEAM']
    df['BS_TEAM%'] = df['BS'] / df['BS_TEAM']
    df['DRV_TEAM%'] = df['DRV'] / df['DRV_TEAM']
    df['REB_TEAM%'] = df['REB'] / df['REB_TEAM']
    df['OREB_TEAM%'] = df['OREB'] / df['OREB_TEAM']
    df['DREB_TEAM%'] = df['DREB'] / df['DREB_TEAM']
    # df['1PTA_TEAM%'] = df['1PTA'] / df['1PTA_TEAM']

    # KAS 
    df['KASTO'] = df.eval('KAS / TO')
    # df['KASFGM'] = df.eval('KAS / FGM') # key assist to made shot ratio
    
    # points distribution
    df['1PTMPTS'] = df.eval(' `1PTM` / PTS')
    df['2PTMPTS'] = df.eval(' 2 * `2PTM` / PTS')
    df['FTMPTS'] = df.eval(' FTM / PTS')
    df['DRV1PTM'] = df.eval(' DRV / `1PTM`')
    df['2PTAFGA'] = df.eval('`2PTA` / FGA') # 2 point attempts per FGA
    
    # per possession
    # df['TOPOS'] = df.eval('TO / POS')
    # df['1PTAPOS'] = df['1PTA'] / df.POS
    # df['2PTAPOS'] = df['2PTA'] / df.POS
    # df['FGAPOS'] = df['FGA'] / df.POS
    # df['PPP'] = df.eval("PTS / POS")
    # df['TFAPOS'] = df.eval('TFA / POS') # fouled per possession
    # df['FTAPOS'] = df.eval('FTA / POS')
    # df['TFPOS'] = df.eval('TF / POS') # foul per possession
    # df['FTTPOS'] = df.eval('(FTA-FTES) / POS') # trip to free throw per possession

    # foul
    # df['TOTF'] = df.eval('TO / TF') # turnover to foul ratio
    # df['BSTF'] = df.eval('BS / TF') # blocked shots to foul ratio
    
    # df['TOTFA'] = df.eval('TO / TFA') # turnover to fouled ratio
    # df['TFTFA'] = df.eval('TF / TFA') # foul to fouled ratio
    # df['FTATFA'] = df.eval('FTA / TFA') # FTA per fouled
    # df['FTESTFA'] = df.eval('FTES / TFA') # extra free throws to fouled ratio
    # df['FTMTFA'] = df.eval('FTM / TFA') # free throw made to fouled ratio
    # df['FTTTFA'] = df.eval('(FTA-FTES) / TFA') # trip to free throw to fouled ratio
    # df['FTESFTA'] = df.eval('FTES / FTA') # extra FT per FTA
    
    df['season'] = season
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