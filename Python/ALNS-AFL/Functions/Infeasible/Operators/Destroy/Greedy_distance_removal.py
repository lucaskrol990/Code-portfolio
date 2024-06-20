'''
This function removes (referee, game)-tuples with the highest distances
Options:
perturb_pct (between 0 and 1): percentage by which to perturb the distances
'''
import numpy as np
import random
def greedy_distance_removal(n, sol, gs, fx, perturb_pct = 0.4):
    destroyed_games = []
    destroyed_refs = []
    distances = sol['trav_dist'].copy()
    distances = [sublist * np.random.uniform(1 - perturb_pct, size = len(sublist)) for sublist in distances]  # Perturb distances
    for i in range(n):
        idx_best = fx['best_index_list'](distances, 'max') # Finds the index of the ref/day combo with highest average distance
        ref = idx_best[0]
        day = idx_best[1]
        distances[idx_best[0]][idx_best[1]] = 0 # Set this distance to 0 now
        games_date = [i for i in sol['ref_assignments'][ref] if gs['game_df'].loc[i, 'date'] == day] # Find games
        # on this date
        idx_remove = random.randint(0, len(games_date) - 1) # Index to remove
        game_remove = games_date[idx_remove] # Game to remove
        destroyed_games.append(game_remove)
        destroyed_refs.append(ref)
        sol = fx['destroy_sol']((ref, game_remove), sol, gs, fx)

    return sol, destroyed_games, destroyed_refs