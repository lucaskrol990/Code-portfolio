'''
This function randomly selects n ride-sharing routes with the highest perturbed ride-sharing distance
Then, it removes the referee with the highest perturbed ride-sharing distance added in the route
'''

import numpy as np
import random

def highest_rs_removal(n, sol, gs, fx, perturb_pct = 0.4):
    destroyed_games = []
    destroyed_refs = []
    for i in range(min(n, gs['ngames'])):
        distances = sol['rs_dist'].copy()
        distances = [sublist * np.random.uniform(1 - perturb_pct, size = len(sublist)) for sublist in distances]  # Perturb distances
        idx_best = fx['best_index_list'](distances, 'max') # Finds the index of the ref/day combo with highest average distance
        ref = idx_best[0]
        day = idx_best[1]
        sel_route = sol['rs_route'][ref][day]
        dists_in_route = [gs['distance_matrix'].iloc[sel_route[i], sel_route[i + 1]] for i in range(len(sel_route) - 1)
                          if sel_route[i] < gs['nrefs']] # Only calculate distances from refs
        dists_in_route = np.random.uniform(1 - perturb_pct, len(dists_in_route)) * np.array(dists_in_route)
        if len(dists_in_route) > 0: # If there is ride-sharing happening
            ref_remove = sel_route[fx['best_index_list'](dists_in_route, 'max')[0]]
        else: # If no ride-sharing happening
            day = random.choice(gs['game_df']['date'])
            # Choose random day (otherwise it might be a day with no assignments at all
            ref_remove = random.choice([refp for refp in range(gs['nrefs']) if sol['assignments_day'][refp][day] > 0])
        games_date = [i for i in sol['ref_day_assignments'][ref_remove][day]] # Find games
        # on this date
        idx_remove = random.randint(0, len(games_date) - 1) # Index to remove
        game_remove = games_date[idx_remove] # Game to remove
        destroyed_games.append(game_remove)
        destroyed_refs.append(ref_remove)
        sol = fx['destroy_sol']((ref_remove, game_remove), sol, gs, fx)

    return sol, destroyed_games, destroyed_refs