'''
This function inserts (referee, game)-tuples with the lowest distances
Options:
perturb_pct (between 0 and 1): percentage by which to perturb the distances
'''
import numpy as np
def greedy_distance_insert(games, sol, gs, fx, perturb_pct = 0.4):
    inserted_refs = []
    for game in games:
        poss_refs = fx['feasible_refs'](game, sol, gs, fx)
        distances = gs['distance_matrix'].iloc[poss_refs, gs['nrefs'] + game].to_numpy()
        distances = np.random.uniform(1 - perturb_pct, size = len(distances)) * distances
        ref_insert = poss_refs[np.argmin(distances)]
        sol = fx['fix_sol']((ref_insert, game), sol, gs, fx)
        inserted_refs.append(ref_insert)
    return sol, inserted_refs, games