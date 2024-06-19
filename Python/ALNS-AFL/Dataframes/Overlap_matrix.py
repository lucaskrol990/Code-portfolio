'''
This function creates a list, indicating per day which match can be paired with which match on the same day, without
giving problems with referees that can not reach the next game in time. An example for 3 games could be:
1 0 1
0 1 0
1 0 1
Which indicates that match 1 and 3 can be performed at the same day without infeasibilities, but a ref assigned to game
2 can never officiate another match on the same day
This would be accessed by [day][game1 idx on this day][game2 index on this day]

An option max_viol is available. This is the percentage of s + w which may be violated at most (for infeasible solutions)
Standard option is 0 (only feasible solutions) or 1/3 for infeasible solutions

For easy accessing, an auxiliary function nu_access is available.
'''
def overlap_matrix(gs, max_viol = 0):
    max_viol = max_viol * (gs['w'] + gs['subtract_start'])
    nu = []
    for day in range(365):
        games = gs['game_df'].index[gs['game_df']['date'] == day].tolist()
        nu.append([])
        if len(games) > 0:  # Only if there are multiple games on this date
            for j in range(len(games)): # Loop through indices of games
                game = games[j] # Current game
                nu[day].append(['error' for _ in range(len(games))]) # Intialize all at a random string to ensure it throws
                                                                # an error when not filled
                nu[day][j][j] = True # This game can always be combined with itself

                # First check if assignments are before or after (or both)
                game_time = gs['game_df'].loc[game, 'time']
                before_idx = [i for i in range(len(games)) if gs['game_df'].loc[games[i], 'time'] <= game_time]
                after_idx = [i for i in range(len(games)) if gs['game_df'].loc[games[i], 'time'] >= game_time]

                # Delete current game from the lists
                before_idx = [i for i in before_idx if i != j]
                after_idx = [i for i in after_idx if i != j]

                if len(before_idx) > 0: # If there are games before this game
                    for idx in before_idx: # For the games before this game
                        game_before = games[idx]
                        end_time = gs['game_df'].loc[game_before, 'time'] + gs['add_end'] + \
                               gs['distance_matrix'].iloc[gs['nrefs'] + game_before, gs['nrefs'] + game] / gs['u']
                        if end_time - max_viol > game_time - gs['subtract_start']: # Arrival time is later than start time
                            nu[day][j][idx] = False
                        else:
                            nu[day][j][idx] = True

                if len(after_idx) > 0: # If there are games after this
                    for idx in after_idx: # For the games after this game
                        game_after = games[idx]
                        start_time = gs['game_df'].loc[game_after, 'time'] - gs['subtract_start']
                        arrival_time = game_time + gs['add_end'] + \
                                       gs['distance_matrix'].iloc[gs['nrefs'] + game, gs['nrefs'] + game_after] / gs['u']
                        if arrival_time - max_viol > start_time:  # Arrival time is later than start time (incl. prep)
                            nu[day][j][idx] = False
                        else:
                            nu[day][j][idx] = True
    return nu