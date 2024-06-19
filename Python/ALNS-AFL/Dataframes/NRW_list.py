'''
This file reads the referee dataframe and tells for every ref if he/she is in NRW or is only here occasionally
In: referee dataframe
Out: NRW_List

Notice:
1. Referees outside of NRW are given the distance 0
'''

from shapely.geometry import Point, Polygon

def NRW_list(referee_df):
    NRW_list = [True for _ in range(referee_df.shape[0])]

    return NRW_list