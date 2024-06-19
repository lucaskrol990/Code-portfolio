'''
This script calculates the statistics for the initial solution provided by the German AFL

Options:
year (int: for which year to calculate the statistic)
'''

year = 2022
from globals_maker import gs_maker
gs = gs_maker(year, False)
from Function_load import function_load
fx = function_load(False)
import pandas as pd
from geopy import distance

def availability_valid(game, ref_id, avail_df):
    date_game = gs['game_df'].loc[game, 'date']  # Date of game
    game_time = gs['game_df'].loc[game, 'time']  # Time of game
    row_idx = ref_id == avail_df['referee']
    row_idx = row_idx.tolist().index(True)
    column_of_strings = avail_df['avail'][row_idx][0:365]  # Take char 1 until 365 of this string (ignore last two)
    av_id = column_of_strings[date_game]  # Availability indicated at this date
    if av_id == 'J' or av_id == '*' or av_id == 'Z':  # Fully available
        # Note: one day in weekend and fallbacks are considered in separate matrices
        return True
    elif av_id == 'M' and game_time <= 13:  # Available until 13:00 and met
        return True
    elif av_id == 'A' and game_time >= 13 and game_time <= 16:  # Available between 13:00 and 16:00 and met
        return True
    elif av_id == 'B' and game_time >= 16:  # Available after 16:00 and met
        return True
    elif av_id == 'D' and game_time <= 16:  # Available before 16:00 and met
        return True
    else:
        return False

def is_fall_back(game, ref_id, avail_df):
    date_game = gs['game_df'].loc[game, 'date']  # Date of game
    row_idx = ref_id == avail_df['referee']
    row_idx = row_idx.tolist().index(True)
    column_of_strings = avail_df['avail'][row_idx][0:365]  # Take char 1 until 365 of this string (ignore last two)
    av_id = column_of_strings[date_game]  # Availability indicated at this date
    if av_id == 'Z':  # Fully available
        # Note: one day in weekend and fallbacks are considered in separate matrices
        return True
    else:
        return False

'''
Finding the assigned referees, both valid and invalid, to the relevant games
'''
# Game assignments can be found from game_df
game_assignments_tmp = [] # Initialize an empty array with length equal to # of games
for i in range(gs['ngames']): # Loop through games
    game_assignments_tmp.append(gs['game_df'].iloc[i, 10:(10 + gs['game_df'].loc[i, 'Number of referees'])].tolist()) # All referees in game

game_assignments = []
refs_invalid = []
for ids in game_assignments_tmp:
    assigned_refs, unconverted_refs = fx['referee_id_to_idx'](ids, gs)
    game_assignments.append(assigned_refs)
    refs_invalid.append(unconverted_refs)

ref_assignments = []
for ref in range(gs['nrefs']):
    ref_assignments.append([])
    for game in range(gs['ngames']):
        if ref in game_assignments[game]:
            ref_assignments[ref].append(game)
print(game_assignments)
print(refs_invalid)
print(ref_assignments)
# # Slack of referees lacking for the game
# nrefs_req = []
# for game in range(gs['ngames']): # Loop through games
#     nrefs_req.append([len(game_assignments[game]) - gs['game_df'].loc[game, 'Number of referees']])
#     # Number of referees missing from required amount
# print(nrefs_req)

'''
First we go through the valid referees and add their distances
'''
trav_dist = 0
for game in range(gs['ngames']): # Loop through games
    trav_dist += gs['distance_matrix'].iloc[game, game_assignments[game]].sum()

print(trav_dist)


'''
Now we go through the invalid referees and add their distances as well as note down their violation (no license or diff association)
'''
# Load in the full referee df (i.e. including refs without a license or from a different association)
referee_df_full = pd.read_csv(f"Datasets/referees_{year}.csv")
referee_df_full = referee_df_full.dropna(axis = 1, how = 'all') # Removes NaN column at the end which appears due to extra delimiter
ref_ids_check = sorted(referee_df_full['id'])

print(f"Number of games is {gs['ngames']}")
print(f"Number of valid referees is {gs['nrefs']}")
print(f"Total number of referees is {referee_df_full.shape[0]}")

non_existent_refs = []
license_viol = 0
diff_association = 0
for game in range(gs['ngames']):
    ref_id_lst = refs_invalid[game]
    for ref_id in ref_id_lst:
        if ref_id not in ref_ids_check:
            non_existent_refs.append(ref_id)
        else:
            row_idx = ref_id == referee_df_full['id']
            row_idx = row_idx.tolist().index(True)
            ref_coords = (referee_df_full.loc[row_idx, 'geoLat'], referee_df_full.loc[row_idx, 'geoLng'])
            game_coords = (gs['game_df'].loc[game, 'geoLat'], gs['game_df'].loc[game, 'geoLng'])
            trav_dist += distance.distance(ref_coords, game_coords).km
            viol = False
            if referee_df_full.loc[row_idx, 'association'] != 1: # Association violation
                diff_association += 1
                viol = True
            if referee_df_full.loc[row_idx, 'license'] != referee_df_full.loc[row_idx, 'license']: # License violation
                license_viol += 1
                viol = True
            if not viol:
                print(f"For referee {ref_id} no violation was found, why was it removed from referee_df?")


'''
Lastly we also measure the violations
'''


# Transform row_idx to referee_idx
ref_ids_ass = [[referee_df_full.loc[row_idx, 'id'] for row_idx in sublist] for sublist in game_assignments]
assigned_ids = [ref_ids_ass[game] + refs_invalid[game] for game in range(gs['ngames'])] # Merge the two lists
assigned_ids = [[i for i in assigned_ids[game] if i not in non_existent_refs] for game in range(gs['ngames'])]
avail_df = pd.read_csv(f"../Datasets/avails_{year}.csv")  # Loading in availability dataset
unique_ids = set([i for sublist in assigned_ids for i in sublist])

ref_assignments_id = {}
for id in unique_ids:
    ref_assignments_id[id] = []
avail_viol = 0
fb_viol = 0
for game in range(gs['ngames']):
    for ref_id in assigned_ids[game]:
        avail_viol += availability_valid(game, ref_id, avail_df)
        ref_assignments_id[ref_id].append(game)
        fb_viol += is_fall_back(game, ref_id, avail_df)

tw_viol = 0
weekend_viol = 0

for ref in range(gs['nrefs']):
    disallowed_days = []
    for idx1 in range(len(ref_assignments[ref])):
        # Time window violation:
        for idx2 in range(idx1, len(ref_assignments[ref])):
            if not gs['nu_matrix'][ref_assignments[ref][idx1]][ref_assignments[ref][idx2]]:
                tw_viol += 1
        # Weekend violation
        if gs['game_df'].loc[ref_assignments[ref][idx1], 'date'] in disallowed_days:
            weekend_viol += 1
        disallowed_days.extend(gs['weekend_list'][ref][gs['game_df'].loc[ref_assignments[ref][idx1], 'date']])

    # for game
    # sol['weekend_viol'][ref] += fx['weekend_overlap'](ref, game, sol, gs, fx)  # If this adds weekend overlap, add it


## Code to compare assignments and availability
# for id in unique_ids:
#     avail_list = []
#     assigned_list = []
#     print('-*' * 50)
#     for game in ref_assignments[id]:
#         date_game = gs['game_df'].loc[game, 'date']  # Date of game
#         game_time = gs['game_df'].loc[game, 'time']  # Time of game
#         row_idx = id == avail_df['referee']
#         row_idx = row_idx.tolist().index(True)
#         column_of_strings = avail_df['avail'][row_idx][0:365]  # Take char 1 until 365 of this string (ignore last two)
#         avail_list.append(column_of_strings[date_game])  # Availability indicated at this date
#         assigned_list.append(date_game) # Date of game
#     print(column_of_strings)
#     print(avail_list)
#     print(assigned_list)

print(f"Total travelled distance in the initial solution is {round(trav_dist)} km")
print(f"A total of {len(non_existent_refs)} referees was assigned which were not in the dataset")
print(f"A total of {license_viol} referees were assigned which were not qualified for officiating the game")
print(f"A total of {diff_association} referees were assigned which did not belong to the association")
print(f"A total of {avail_viol} availability violations were found in this assignment")
print(f"A total of {fb_viol} fall-back violations were found in this assignment")
print(f"A total of {tw_viol} time-window violations were found in this assignment")
print(f"A total of {weekend_viol} weekend violations were found in this assignment")
viol_cost = gs['penalty_tw'] * tw_viol + gs['penalty_avail'] * avail_viol + gs['penalty_weekend'] * weekend_viol + \
           gs['penalty_gamma'] * sum([8 - len(ref_assignments_id[id]) for id in unique_ids if len(ref_assignments_id[id]) < 8]) +\
            gs['penalty_fb'] * (gs['max_fb'] - fb_viol)
print(f"Total violation costs equal {round(viol_cost)}")
viol_cost += (license_viol + diff_association) * gs['penalty_hire']
print(f"Total violation costs equal including for hire refs {round(viol_cost)}")
print(f"Objective value equals {round(viol_cost + trav_dist)}")
print(f"A total of {sum([8 - len(ref_assignments_id[id]) for id in unique_ids if len(ref_assignments_id[id]) < 8])} gamma violations were found")
print(f"Sum of {sum([len(x) for x in assigned_ids])} assignments")

