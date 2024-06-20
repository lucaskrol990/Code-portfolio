'''
This function finds the referees which have violations (penalty cost > 0) and removes in total n games from them
'''

import random

def random_violation_removal(n, sol, gs, fx):
    games = []
    destroyed_refs = []
    for _ in range(n):
        # Destroy a random violation
        if len(sol['violation_pairs']) > 0:
            ref, game = random.choice(sol['violation_pairs'])
        else:
            # Use random destroy
            # Create a weighted list of indices (to prevent choosing from refs with less assignments relatively more often)
            weighted_indices = []
            for ref in range(gs['nrefs']):
                if sol['penalty_cost'][ref] > 0:
                    weighted_indices.extend([ref] * len(sol['ref_assignments'][ref])) # Adds this ref for the number of games he/she has
            if len(weighted_indices) == 0: # Nothing with penalty
                weighted_indices = [index for index, sublist in enumerate(sol['ref_assignments']) for _ in range(len(sublist))]
            ref = random.choice(weighted_indices) # Chooses the referee
            game = random.choice(sol['ref_assignments'][ref]) # Chooses the assigned game

        games.append(game) # Save that this game needs a repair later
        destroyed_refs.append(ref)
        sol = fx['destroy_sol']((ref, game), sol, gs, fx) # Destroys this referee-game tuple from the solution

    return sol, games, destroyed_refs