'''
Checks if time windows of the games do not overlap, i.e. the next game start time is before previous game end time + transport
Note: in the infeasible version, we check using overlap_matrix_violation, since violations are allowed to some extend
'''
def feasibility_2(sol, gs, fx):
    n_infeasibilities = 0
    for ref in range(gs['nrefs'] - 1): # Ignore the for-hire ref
        assignments = sol['ref_assignments'][ref] # Assigned games
        for game1 in assignments:
            for game2 in assignments:
                if not gs['nu_matrix_prime'][game1][game2]: # Violation of time window
                    n_infeasibilities += 1
                    print(f"Infeasible: There is overlap between game {game1} and game {game2} for referee"
                          f"ref {ref}")

    return n_infeasibilities
