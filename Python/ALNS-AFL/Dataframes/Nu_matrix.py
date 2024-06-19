'''
This function creates a matrix which indicates for all games if there would be overlap violations if refs were assigned
to this game combination

Option:
max_viol (maximum violation of time window)
'''

def nu_matrix(gs, max_viol = 0):
    max_viol = max_viol * (gs['w'] + gs['subtract_start'])
    nu_matrix = []
    for game in range(gs['ngames']):
        nu_matrix.append([True for _ in range(gs['ngames'])]) # In first instance, all games are ok
        day = gs['game_df'].loc[game, 'date']
        same_day_games = [idx for idx in range(gs['ngames']) if gs['game_df'].loc[idx, 'date'] == day and idx != game]
        if len(same_day_games) == 0:
            pass # Do nothing, all games can be combined with this game
        else:
            game_time = gs['game_df'].loc[game, 'time']
            before_idx = [i for i in same_day_games if gs['game_df'].loc[i, 'time'] <= game_time]
            after_idx = [i for i in same_day_games if gs['game_df'].loc[i, 'time'] >= game_time]

            # Check if there is overlap between end time of previous game (if any) and start time of new game
            if len(before_idx) > 0:
                for idx in before_idx:  # For the games before this game
                    end_time = gs['game_df'].loc[idx, 'time'] + gs['add_end'] + \
                               gs['distance_matrix'].iloc[gs['nrefs'] + idx, gs['nrefs'] + game] / gs['u']
                    if end_time - max_viol > game_time - gs['subtract_start']:  # Arrival time is later than start time
                        nu_matrix[game][idx] = False # There is a violation then
                    else:
                        nu_matrix[game][idx] = True

            # Check if there is overlap between start time of next game (if any) and arrival time when coming from this game
            if len(after_idx) > 0:  # If there are games after this
                for idx in after_idx:  # For the games after this game
                    start_time = gs['game_df'].loc[idx, 'time'] - gs['subtract_start']
                    arrival_time = game_time + gs['add_end'] + \
                                   gs['distance_matrix'].iloc[gs['nrefs'] + game, gs['nrefs'] + idx] / gs['u']
                    if arrival_time - max_viol > start_time:  # Arrival time is later than start time (incl. prep)
                        nu_matrix[game][idx] = False # There is a violation then
                    else:
                        nu_matrix[game][idx] = True
    return nu_matrix
