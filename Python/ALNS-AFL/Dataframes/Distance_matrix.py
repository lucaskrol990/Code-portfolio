'''
This file reads the game and referee dataframe and constructs a distance matrix based on their values
In: referee dataframe + game dataframe
Out: distance matrix

Notice: 
1. Referees outside of NRW are given the distance 0
'''

import pandas as pd
from geopy import distance
from shapely.geometry import Point, Polygon

def distance_matrix_creator(referee_df, game_df):
    referee_tuples = [(referee_df.loc[i, 'geoLat'], referee_df.loc[i, 'geoLng']) for i in range(referee_df.shape[0])]
    game_tuples = [(game_df.loc[i, 'geoLat'], game_df.loc[i, 'geoLng']) for i in range(game_df.shape[0])]
    locations_tuples = referee_tuples + game_tuples

    distance_lists = []
    for i in range(len(locations_tuples)):
        distance_lists.append([])
        for j in range(len(locations_tuples)):
            distance_lists[i].append(distance.distance(locations_tuples[i], locations_tuples[j]).km)

    distance_matrix = pd.DataFrame(distance_lists)
    return distance_matrix