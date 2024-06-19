'''
This function returns a dataframe displaying per (ref, match) combination of the assignment of the referee to that match
is allowed based on the league requirements (part of Feasibility check 4).

4. Officials may only officiate games within their allowed leagues
- t1 match requires only t1 official
- t2 match requires only t2 official
- leagues not in "own team" require that official is not officiating a match of his/her own team
'''
import pandas as pd
import re


def valid_assignments(gs):
    valid_assignment = []
    for ref in range(gs['nrefs']):
        valid_assignment.append([])
        for game in range(gs['ngames']):
            if gs['game_df'].loc[game, 'offownc'] > 0: # Ot game
                valid_assignment[ref].append(True)  # So always valid referee
            elif gs['game_df'].loc[game, 'toplev1'] > 0: # t1 game
                if gs['referee_df'].loc[ref, 'GFL']:  # Referee may officiate t1 games
                    valid_assignment[ref].append(True)  # So valid
                else:
                    valid_assignment[ref].append(False)  # Invalid
            elif gs['game_df'].loc[game, 'toplev2'] > 0: # t2 game
                if gs['referee_df'].loc[ref, 'GFL2']: # Referee may officiate t2 games
                    valid_assignment[ref].append(True)  # So valid
                else:
                    valid_assignment[ref].append(False)  # Invalid
            elif not same_club(ref, game, gs):
                valid_assignment[ref].append(True)  # So valid
            else:
                valid_assignment[ref].append(False) # Invalid assignment
    return valid_assignment


'''
This function determines if a referee is from the same club as clubs playing in the match
'''
def same_club(ref_idx, match_idx, gs):
    ref_club = gs['referee_df'].loc[ref_idx, 'club']
    if ref_club == -1: # If referee has no club, they can never be of the same club
        return False

    ## First find the clubs in the match
    club_ids_in_match = [gs['game_df'].loc[match_idx, f'club{i}'] for i in range(1, 5)]

    ## Now check if club of referee is in list of clubs in the match
    return ref_club in club_ids_in_match