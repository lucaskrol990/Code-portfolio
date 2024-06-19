import pandas as pd

'''
This file reads the referee dataset for a specific year and returns a dataframe with the data required for the ALNS algorithm
In: year
Out: referee dataframe
'''

def referee_df_creator(inst):
    referee_df = pd.read_csv(f"Datasets/Gabor/referees_Gabor_{inst}.csv")
    # Remove irrelevant columns from dataframe
    referee_df = referee_df.dropna(axis = 1, how = 'all') # Removes NaN column at the end which appears due to extra delimiter
    # del referee_df["dob"]
    # del referee_df["street"]
    # del referee_df["town"]
    # del referee_df["plz"]
    # del referee_df["FLAG"]
    # Remove referees which are not relevant to the case
    referee_df = referee_df[referee_df['association'] == 1] # Only the ones with association 1 are relevant
    referee_df = referee_df[referee_df['license'] == referee_df['license']]
    # No license = no officiating, we check this by looking if the license values equal each other: if not, NaN

    # Resetting the index
    referee_df.reset_index(drop = True, inplace = True)
    # del referee_df["index"]

    return referee_df