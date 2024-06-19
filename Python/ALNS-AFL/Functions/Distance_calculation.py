'''
This function calculates the total travelled distance + ride-sharing distance of a referee
based on a start location, end location and indices of ride-sharing other referees

Note: this version excludes ride sharing!
'''

def distance_calculation(ref, start_loc, end_loc, sol, gs):
    return gs['distance_matrix'].iloc[start_loc, end_loc]

def time_calculation(ref, start_loc, end_loc, sol, gs):
    return gs['distance_matrix'].iloc[start_loc, end_loc] / gs['u']


