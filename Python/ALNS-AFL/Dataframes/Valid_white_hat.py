'''
This function returns a matrix containing T/F about if the referee would be a valid white for the given match.
This is based on the following rules:
White hat requirements
- t1 match requires at least a t1+wh official
- t2 match requires at least a t2+wh official
- whp match requires at least a wh official
- other matches (not t1/t2/whp) require at least a wh/whp official

'''
import pandas as pd

def valid_white_hat(gs):
    # Loop through referees and games to see if a white hat assignment would be valid
    valid_wh_list = []
    for ref in range(gs['nrefs']):
        valid_wh_list.append([])
        for game in range(gs['ngames']):
            if gs['game_df'].loc[game, 'toplev1'] == 1: # If t1 game
                if gs['referee_df'].loc[ref, 'GFL'] and gs['referee_df'].loc[ref, 'HSR']: # Check if t1 + wh
                    valid_wh_list[ref].append(True)
                else:
                    valid_wh_list[ref].append(False)
            elif gs['game_df'].loc[game, 'toplev2'] == 1: # If t2 game
                if gs['referee_df'].loc[ref, 'GFL2'] and gs['referee_df'].loc[ref, 'HSR']: # Check if t2 + wh
                    valid_wh_list[ref].append(True)
                else:
                    valid_wh_list[ref].append(False)
            elif gs['game_df'].loc[game, 'whprosp'] == 1: # If part of other matches (whp allowed)
                if gs['referee_df'].loc[ref, 'HSR'] or gs['referee_df'].loc[ref, 'HSRP']: # Check if wh or whp
                    valid_wh_list[ref].append(True)
                else:
                    valid_wh_list[ref].append(False)
            else: # Must then be part of no whp allowed match
                if gs['referee_df'].loc[ref, 'HSR']: # Check if wh
                    valid_wh_list[ref].append(True)
                else:
                    valid_wh_list[ref].append(False)


    return valid_wh_list