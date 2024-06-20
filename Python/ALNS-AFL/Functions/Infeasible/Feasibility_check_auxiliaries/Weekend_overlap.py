'''
Checks for a given game if other assignments of the referee would lead to weekend violations
'''

def weekend_overlap(ref, game, sol, gs, fx):
    overlap = 0
    day_game = gs['game_df'].loc[game, 'date'] # Days of assignments
    if len(gs['weekend_list'][ref][day_game]) > 0: # If there is a restriction on this date
        for day_restric in gs['weekend_list'][ref][day_game]: # Loop through restricted dates
            overlap += sol['assignments_day'][ref][day_restric] # How often the referee is assigned at a restricted date

    return overlap