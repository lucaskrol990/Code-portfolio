'''
This function creates a matrix denoting per ref-game combination of the referee is available to officiate for
the given game.
In: gs (specifically game_df)
Out: availability_matrix

Note: H added here to indicate availability from 13 onwards
'''
import pandas as pd

def availability_matrix(gs, Feasible, inst):
    avail_df = pd.read_csv(f"Datasets/avails_Gabor_{inst}.csv")  # Loading in availability dataset
    avail_df = pd.merge(gs['referee_df'], avail_df, left_on="id", right_on="referee", how="left")
    availability_matrix = []  # Will contain when the referee is (partially) available for all referees

    if Feasible: # No for hire referee added as last entry
        nrefs = avail_df.shape[0]
    else: # For hire referee added as last entry
        nrefs = avail_df.shape[0] - 1

    for ref in range(nrefs):
        column_of_strings = avail_df['avail'][ref]
        availability_matrix.append([]) # Empty for this referee until now

        for game in range(gs['ngames']): # Loop through games
            date_game = gs['game_df'].loc[game, 'date'] # Date of game
            game_time = gs['game_df'].loc[game, 'time'] # Time of game
            av_id = column_of_strings[date_game] # Availability indicated at this date

            if av_id == 'J' or av_id == '*' or av_id == 'Z': # Fully available
                # Note: one day in weekend and fallbacks are considered in separate matrices
                availability_matrix[ref].append(True)
            elif av_id == 'M' and game_time <= 13: # Available until 13:00 and met
                availability_matrix[ref].append(True)
            elif av_id == 'A' and game_time >= 13 and game_time <= 16: # Available between 13:00 and 16:00 and met
                availability_matrix[ref].append(True)
            elif av_id == 'B' and game_time >= 16: # Available after 16:00 and met
                availability_matrix[ref].append(True)
            elif av_id == 'D' and game_time <= 16: # Available before 16:00 and met
                availability_matrix[ref].append(True)
            elif av_id == 'H' and game_time >= 13: # Available after 16:00 and met
                availability_matrix[ref].append(True)
            else:
                availability_matrix[ref].append(False)

    if not Feasible:  # Add additional entry with only true for psuedo ref
        availability_matrix.append([True] * gs['ngames'])

    return availability_matrix