'''
This function calculates per match the maximum amount of people with E license, based on the following rules:
- If t1/t2 or (Regionalliga and division senior):
    - E = 0
- If cup and # participating teams < 3:
    - E <= 1
- Else:
    - E <= 2

It does so by:
1. Calculating the relevant league sets
2. Looping through the games in game_df:
    - If in E0 league set, max_E = 0
    - If in E1 league set, check # participating teams
        - If # participating teams < 3: max_E = 1
        - Else max_E = 2
    - Else max_E = 2
'''
import pandas as pd
def license_requirement(gs):
    ## Looping through games:
    max_E = []
    for game in range(gs['ngames']):
        if gs['game_df'].loc[game, 'toplev1'] == 1 or gs['game_df'].loc[game, 'toplev2'] == 1:
            max_E.append(0)
        elif gs['game_df'].loc[game, 'cupmode'] != 0:
            visitor_str = str(gs['game_df'].loc[game, 'visitor'])
            nteams = sum([1 for i in range(1, 5) if gs['game_df'].loc[game, f'club{i}'] != -1])
            if nteams <= 3:
                max_E.append(1)
            else:
                max_E.append(2)
        else:
            max_E.append(2)

    return max_E