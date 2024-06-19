'''
This file creates the "globals" that are often passed as argument to functions.
Note: some things are loaded from file to reduce computational time, originally they were calculated with one of the
related methods in the folder Dataframes. Notice: the construction method is in an if statement now

Options:
- compute_new_dfs (T/F): indicates if you want to compute new dataframes (which can be loaded from file later)
- feasible (T/F): indicates if you want to create globals which together constitute a feasible solution

Note: for infeasible creation we assume an additional referee is available, at index nrefs, which has all capabilities
This is an indicator that an outside referee was hired.
'''
feasible = False

import pandas as pd
import numpy as np
from Dataframes.Gabor.Referees import referee_df_creator
from Dataframes.Gabor.Match import game_df_creator
from Dataframes.Gabor.License_requirements import license_requirement
from Dataframes.Gabor.White_hats_needed import white_hats_needed
from Dataframes.Gabor.Availability_matrix import availability_matrix
from Dataframes.Gabor.Overlap_matrix import overlap_matrix
from Dataframes.Gabor.Nu_matrix import nu_matrix
from Dataframes.Gabor.Weekend_restriction import weekend_restriction
from Dataframes.Gabor.Fall_back_matrix import fall_back_matrix
from Dataframes.Gabor.NRW_list import NRW_list


def gs_maker(inst):
      compute_new_dfs = False
      if compute_new_dfs:
            # If we wish to calculate new dataframes which can be loaded from file, you can use this structure
            # !!Note you need to indent all stuff coming after print(year) to the same tab indent then!!
            from Dataframes.Gabor.Distance_matrix import distance_matrix_creator
            from Dataframes.Gabor.Valid_white_hat import valid_white_hat
            from Dataframes.Gabor.Valid_assignments import valid_assignments
            for inst in range(1, 11):
                  print(inst)

      referee_df = referee_df_creator(inst)
      game_df = game_df_creator(inst)

      # Add the "to be hired" referee:
      referee_df.loc[referee_df.shape[0]] = {'id': -1, 'association': 1, 'license': 'A', 'reqgames': 0, 'club': -1,
                                             'HSR': True, 'HSRP': True, 'EFAF': True, 'GFL': True, 'GFL2': True,
                                             'mobility': False, 'geoLat': 50, 'geoLng': 6}

      nrefs = referee_df.shape[0]
      ngames = game_df.shape[0]

      # Hyper parameters
      w = 0.5
      add_end = 2.5 + w # End time is 2.5h for game + 0.5 hour for wrap up
      subtract_start = 1 # 1 hour set-up time
      u = 50 # Travel speed (50km/u)
      m = 0.1 # At most 10% travel time added
      kappa = [3 * referee_df.loc[ref, 'mobility'] for ref in range(nrefs)] # At most 4 referees per car (so can offer up to 3)

      gs = {'referee_df': referee_df,
            'game_df': game_df,
            'nrefs': nrefs,
            'ngames': ngames,
            'w': w,
            'add_end': add_end,
            'subtract_start': subtract_start,
            'u': u,
            'm': m,
            'kappa': kappa}

      gs['availability_matrix'] = availability_matrix(gs, False, inst)
      gs['weekend_list'] = weekend_restriction(gs, False)
      gs['fb_list'] = fall_back_matrix(gs, False)

      if compute_new_dfs:
            distance_matrix = distance_matrix_creator(referee_df, game_df)
            gs['distance_matrix'] = distance_matrix
            distance_matrix.to_csv(f"Datasets/Gabor/distance_matrix_{inst}.csv", index = False)
            valid_wh = valid_white_hat(gs)
            valid_wh_df = pd.DataFrame(valid_wh)
            gs['valid_wh'] = valid_wh
            valid_wh_df.to_csv(f"Datasets/Gabor/valid_wh_{inst}.csv", index=False)
            valid_ass = valid_assignments(gs)
            valid_ass_df = pd.DataFrame(valid_ass)
            gs['valid_assignments'] = valid_ass
            valid_ass_df.to_csv(f"Datasets/Gabor/valid_assignments_{inst}.csv", index=False)



      gs['distance_matrix'] = pd.read_csv(f"Datasets/Gabor/distance_matrix_{inst}.csv")

      gs['NRW_list'] = NRW_list(gs['referee_df'])

      if feasible: # All values are representative, so just take max
            gs['max_dist'] = np.max(gs['distance_matrix'].values)
      else: # Value of to hire referee should be removed
            idx = [i for i in range(gs['nrefs'] + gs['ngames']) if i != gs['nrefs']]
            gs['max_dist'] = np.max(gs['distance_matrix'].iloc[idx, idx].values)

      gs['valid_wh'] = pd.read_csv(f"Datasets/Gabor/valid_wh_{inst}.csv", index_col = False).values.tolist()
      gs['valid_assignments'] = pd.read_csv(f"Datasets/Gabor/valid_assignments_{inst}.csv", index_col = False).values.tolist()
      gs['overlap_matrix'] = overlap_matrix(gs)
      gs['overlap_matrix_violation'] = overlap_matrix(gs, 1/3)

      gs['license_requirements'] = license_requirement(gs) # Calculates max E refs per game
      gs['wh_needed'] = white_hats_needed(gs)
      gs['nu_matrix'] = nu_matrix(gs)
      gs['nu_matrix_prime'] = nu_matrix(gs, 1/3)

      if not feasible:
            # For infeasible, we also create globals to save penalty costs
            gs['penalty_tw'] = gs['max_dist']
            gs['penalty_avail'] = 2 * gs['max_dist']
            gs['penalty_hire'] = 10 * gs['max_dist']
            gs['penalty_gamma'] = 0.5 * gs['max_dist']
            gs['penalty_fb'] = gs['max_dist']
            gs['max_fb'] = 20 # In total
            gs['penalty_weekend'] = gs['max_dist']

      return gs

gs_maker(1)