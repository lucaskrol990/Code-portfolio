import pandas as pd
'''
This file reads the game dataset for a specific year and returns a dataframe with the data required for the ALNS algorithm
In: year
Out: game dataframe

Notice: 
1. Mistake in the csv of games, ref05 is, in error, forgotten, which means that the 12th referee has no column header
2. Some games have more than 12 referees, for now these games are skipped (with on_bad_lines = 'skip')
'''
def game_df_creator(inst):
    '''
    This version keeps the referees which are assigned
    '''
    game_df = pd.read_csv(f"Datasets/games_Gabor_{inst}.csv", on_bad_lines= 'skip', index_col = False)
    # Remove irrelevant columns from dataframe
    game_df = game_df.dropna(axis = 1, how = 'all') # Removes NaN column at the end which appears due to extra delimiter

    game_df.reset_index() # Reset index

    ## Calculate the number of referees required per game
    game_df['Number of referees'] = game_df['num_offs']
    game_df.reset_index(drop = True, inplace = True)

    # Transform dates to day of the year
    game_df['date'] = game_df['day'] - 1
    del game_df['day']

    return game_df