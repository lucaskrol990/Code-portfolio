'''
This function creates a list of lists indicating per referee per game if this is a fallback assignment or not
This is useful in checking if the total number of fall back assignments per referee is below the maximum

Accessing: [ref][game] -> yields binary (True if fall back, False if no fall back (so not equal to 'Z'))

Options:
Feasible (if infeasible, for ref referee needs to be skipped in gs)

'''

import pandas as pd

def fall_back_matrix(gs, Feasible):
    fb_list = [[False for _ in range(gs['ngames'])] for _ in range(gs['nrefs'])]

    return fb_list