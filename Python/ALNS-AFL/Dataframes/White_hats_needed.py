'''
Calculates the minimum number of white hat (or white hat prospects, depending on valid_white_hat) needed per game
Basically, this boils down to identifying if the match is cup and has more than 3 teams (2 needed) else 1.
'''
import pandas as pd

def white_hats_needed(gs):
    wh_needed = []
    for game in range(gs['ngames']):
        if gs['game_df'].loc[game, 'cupmode'] == 1: # If cup match
            nteams = sum([1 for i in range(1, 5) if gs['game_df'].loc[game, f'club{i}'] != -1])
            if nteams > 3:
                wh_needed.append(2)
            else:
                wh_needed.append(1)
        else:
            wh_needed.append(1)
        if wh_needed[game] > gs['game_df'].loc[game, 'Number of referees']:
            wh_needed[game] = gs['game_df'].loc[game, 'Number of referees']
    return wh_needed


