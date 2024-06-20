'''
15. Base distance always equal distance of assigned games
'''

def feasibility_15(sol, gs, fx):
    n_infeasibilities = 0
    for ref in range(gs['nrefs']):
        if gs['NRW_list'][ref]: # Only for the ones in NRW
            for day in range(365):
                route_no_rs = [ref] + [gs['nrefs'] + game for game in sol['ref_day_assignments'][ref][day]] + [ref]
                trav_dist_base = sum([gs['distance_matrix'].iloc[route_no_rs[i], route_no_rs[i + 1]] for i in range(len(route_no_rs) - 1)])
                if abs(trav_dist_base - sol['assignments_base_dist'][ref][day]) > 0.01:  # If distances do not align
                    print(f"Infeasible: referee {ref} had base_dist = {sol['assignments_base_dist'][ref][day]} "
                                    f"but it should be {trav_dist_base}")

    return n_infeasibilities