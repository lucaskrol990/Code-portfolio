'''
10. Ride sharing only happens if referees are assigned to the same game
'''

def feasibility_10(sol, gs, fx):
    n_infeasibilities = 0
    for ref in range(gs['nrefs']):
        for day in range(365):
            if len(sol['rs_given'][ref][day]) > 0: # If referee offered ride-sharing
                for ref_prime in sol['rs_given'][ref][day]: # Loop through refs which received ride-sharing
                    if set(sol['ref_day_assignments'][ref][day]) != set(sol['ref_day_assignments'][ref_prime][day]):
                        print(f"Referee {ref} did not have the same assignment as referee {ref_prime}, but yet"
                              f"they were involved in the same ride-sharing, which is given as:")
                        print(sol['rs_route'][ref][day])
                        n_infeasibilities += 1

    return n_infeasibilities