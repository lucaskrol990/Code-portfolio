'''
This function randomly inserts n (referee, game) tuples in the solution
'''
import random

def random_insertion(games_arg, sol, gs, fx):
    refs_assigned = []
    games_assigned = []
    # Insert randomly
    if type(games_arg) == list:
        games = games_arg.copy()
        for _ in range(len(games)):
            idx = random.choice(range(len(games))) # Randomly choosen index
            game = games[idx] # This is the corresponding game
            games_assigned.append(game)
            del games[idx] # Can now be removed from the list
            poss_refs = fx['feasible_refs'](game, sol, gs, fx) # Find the feasible refs for the game
            if len(poss_refs) == 1:
                ref = poss_refs[0]
            else:
                ref = random.choice(poss_refs)  # Chooses the referee
            sol = fx['fix_sol']((ref, game), sol, gs, fx) # Repair the solution with this (ref, game) tuple
            refs_assigned.append(ref)
    else:
        poss_refs = fx['feasible_refs'](games_arg, sol, gs, fx)  # Find the feasible refs for the game
        if len(poss_refs) == 1:
            ref = poss_refs[0]
        else:
            ref = random.choice(poss_refs)  # Chooses the referee
        sol = fx['fix_sol']((ref, games_arg), sol, gs, fx)  # Repair the solution with this (ref, game) tuple
        refs_assigned.append(ref)
    return sol, refs_assigned, games_assigned