'''
This function creates a list of lists of lists indicating per referee per date which others dates are disallowed to contain games
This can make checking if the referee is assigned only one of the days in the weekend easier

Accessing: [ref][date] -> yields list of disallowed dates (empty for most ref-date combinations)

Options:
Feasible (if infeasible, for ref referee needs to be skipped in gs)

Notice: sometimes thursdays are also included as a day of the weekend, therefore we check for * in the upcoming three days
'''

import pandas as pd

def weekend_restriction(gs, Feasible):
    wkd_list = [[[] for _ in range(gs['game_df'].loc[gs['ngames'] - 1, 'date'] + 1)] for _ in range(gs['nrefs'])]  # Will be the return value

    return wkd_list