'''
This function goes through the removed game, determines the feasible referees and selects 1 out of the n refs with lowest assignments
to award it to
'''
import random
import heapq

def least_assignment_insertion(removed_games, sol, gs, fx, m = None):
    if m == None: # Nothing specified
        m = len(removed_games) # Default options of n

    inserted_refs = [] # Stores which refs are assigned to the game
    for game in removed_games:
        feasible_refs = fx['feasible_refs'](game, sol, gs, fx)
        m_cur = min(m, len(feasible_refs))
        least_ass_refs = heapq.nlargest(m_cur, feasible_refs, key=
            sol['gamma_viol'].__getitem__) # Choose m referees with lowest ass
        ref = random.sample(least_ass_refs, 1)[0] # Choose 1 to assign
        inserted_refs.append(ref)
        sol = fx['fix_sol']((ref, game), sol, gs, fx)

    return sol, inserted_refs, removed_games