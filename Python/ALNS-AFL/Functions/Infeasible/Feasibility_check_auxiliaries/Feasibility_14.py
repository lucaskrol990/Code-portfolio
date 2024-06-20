'''
14. Ride-sharing distances of routes equal distance of trav_dist
'''

def feasibility_14(sol, gs, fx):
    n_infeasibilities = 0
    for ref in range(gs['nrefs']):
        for day in range(365):
            if len(sol['rs_given'][ref][day]) > 0:  # If ride-sharing is given
                return_0 = sol['trav_dist'][ref][day] * sol['assignments_day'][ref][day]
                return_1 = sum([gs['distance_matrix'].iloc[sol['rs_route'][ref][day][i],
                                sol['rs_route'][ref][day][i + 1]] for i in range(len(sol['rs_route'][ref][day]) - 1)])
                if abs(return_1 - return_0) > 0.01:
                    print(f"Infeasible: According to sol the distance travelled equals {return_0}"
                                    f" but it should actually equal {return_1}. Check for ride share givers")
            elif sol['rs_received'][ref][day] != -1: # If ref received ride-sharing
                if sol['trav_dist'][ref][day] != 0: # So distance should be zero
                    print(f"Infeasible: referee {ref} was ride-sharing but incurred trav_dist = {sol['trav_dist'][ref][day]}")
            else: # No ride-sharing received, so should be base distance
                if abs(sol['trav_dist'][ref][day] * sol['assignments_day'][ref][day] - sol['assignments_base_dist'][ref][day]) > 0.01:
                    print(f"Infeasible: referee {ref} had base_dist = {sol['assignments_base_dist'][ref][day]} "
                                    f"but trav_dist = {sol['trav_dist'][ref][day] * sol['assignments_day'][ref][day]}")
    return n_infeasibilities