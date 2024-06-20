'''
This function inserts (referee, game)-tuples with the aim to insert referees such that they have the same set of assignments
as another referee (hopefully opening up the possibility for ride-sharing)
'''
import numpy as np
def same_assignment_insertion(games, sol, gs, fx):
    inserted_refs = []
    for game in games:
        # First find all sets of assignments
        day_game = gs['game_df'].loc[game, 'date']
        ass_set_date = [] # Will store all sets of assignments that are present on this date
        for ref in range(gs['nrefs']):
            if sol['assignments_day'][ref][day_game] > 0:
                if sol['ref_day_assignments'][ref][day_game] not in ass_set_date:
                    ass_set_date.append(sol['ref_day_assignments'][ref][day_game])

        # Then find all feasible referees
        poss_refs = fx['feasible_refs'](game, sol, gs, fx)

        # Then find a referee which can then yield a set of assignments the same as another referee
        found_ref = False
        for ref in poss_refs:
            if sorted(sol['ref_day_assignments'][ref][day_game] + [game]) in ass_set_date:
                ref_insert = ref
                found_ref = True
                break

        if not found_ref: # If no ref can be found which yields the same assignment set, look for min dist ass
            dists = gs['distance_matrix'].iloc[poss_refs, gs['nrefs'] + game].to_numpy()
            for i in range(len(poss_refs)):
                if sol['rs_dist'][poss_refs[i]][day_game] > 0: # If the referee has ride-sharing already
                    dists[i] = 10000 # We set the distance high such that assignment to this ref is disfavoured
            ref_insert = poss_refs[np.argmin(dists)]


        sol = fx['fix_sol']((ref_insert, game), sol, gs, fx)
        inserted_refs.append(ref_insert)
    return sol, inserted_refs, games