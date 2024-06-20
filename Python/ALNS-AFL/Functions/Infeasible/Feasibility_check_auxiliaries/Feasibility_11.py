'''
11. Ride sharing only happens if additional distance for ride sharing offerer is less than m%
'''

def feasibility_11(sol, gs, fx):
    n_infeasibilities = 0
    for ref in range(gs['nrefs']):
        for day in range(365):
            if len(sol['rs_given'][ref][day]) > 0:  # If ride-sharing is given
                if sol['rs_dist'][ref][day] - (1 + gs['m']) * sol['assignments_base_dist'][ref][day] > 1:
                    print(f"Referee {ref} offered ride-sharing on day {day} but this exceeded m%")
                    n_infeasibilities += 1
    return n_infeasibilities