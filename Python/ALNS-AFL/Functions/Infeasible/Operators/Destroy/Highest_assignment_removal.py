'''
This function selects n referees out of the m referees with the most assignments and randomly removes 1 game of them

'''
import random
import heapq

def highest_assignment_removal(n, sol, gs, fx, m = None):
    max_removals = sum([len(sol['ref_assignments'][ref]) > 0 for ref in range(gs['nrefs'])])
    if m == None: # Nothing specified
        m = min(2 * n, max_removals) # Default options of 2 times n
    highest_ass_refs = heapq.nsmallest(m, range(len(sol['gamma_viol']) - 1), key=
            sol['gamma_viol'].__getitem__) # Choose m referees with highest ass (removed for hire)
    destroyed_refs = random.sample(highest_ass_refs, min(n, max_removals)) # Choose n out of m referees to destroy
    destroyed_games = [random.sample(sol['ref_assignments'][ref], 1)[0] for ref in destroyed_refs] # Select a random game of them
    for i in range(n): # Actually destroy this from the solution
        sol = fx['destroy_sol']((destroyed_refs[i], destroyed_games[i]), sol, gs, fx)
    return sol, destroyed_games, destroyed_refs