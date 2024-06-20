'''
This function randomly removes n (referee, game) tuples from the solution
'''
import random

def random_removal(n, sol, gs, fx):
    games = []
    destroyed_refs = []
    for _ in range(n):
        # Destroy randomly
        # Create a weighted list of indices (to prevent choosing from refs with less assignments relatively more often)
        weighted_indices = [index for index, sublist in enumerate(sol['ref_assignments']) for _ in range(len(sublist))]
        ref = random.choice(weighted_indices) # Chooses the referee
        game = random.choice(sol['ref_assignments'][ref]) # Chooses the assigned game
        games.append(game) # Save that this game needs a repair later
        destroyed_refs.append(ref)
        sol = fx['destroy_sol']((ref, game), sol, gs, fx) # Destroys this referee-game tuple from the solution

    return sol, games, destroyed_refs