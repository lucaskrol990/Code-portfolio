'''
9. Ride sharing capacity is met at all times
'''

def feasibility_9(sol, gs, fx):
    n_infeasibilities = 0
    for ref in range(gs['nrefs']):
        for day in range(365):
            if len(sol['rs_given'][ref][day]) > gs['kappa'][ref]:  # If ride-sharing capacity is exceeded
                print(f"Infeasible: Referee {ref} had a total of {len(sol['rs_given'][ref][day])} passengers, but could "
                      f"only take {gs['kappa'][ref]} passengers with him, oops!")
                n_infeasibilities += 1

    return n_infeasibilities