'''
This function determines for a ref, second ref and game if they could rideshare to the same game (in terms of distance added < m%)
Output:
[0] List of new route (empty if no ride sharing)
[1] New distance


We do this as follows:
First we check if the two referees have the exact same assignment set on this day
If not:
    return [], 10000 ==> they can not ride share together

Then we check if one of the two referees already offers ridesharing to this game
    if both do:
        return [], 10000 ==> we do not want them to combine the routes
    if one does:
        check all possible new entries of the other referee in the tour
        return [new route], new_dist
    else:
        compare distance of ref - ref_prime - game - ref_prime - ref to ref_prime - ref - game - ref - ref_prime
        return [new route], new_dist
'''

def rs_possible_distance(ref, ref_prime, game, sol, gs, fx):
    day_game = gs['game_df'].loc[game, 'date']
    ass_day_ref = sol['ref_day_assignments'][ref][day_game]
    ass_day_ref_prime = sol['ref_day_assignments'][ref_prime][day_game]

    if not gs['NRW_list'][ref] or not gs['NRW_list'][ref_prime]: # If one of the refs is outside NRW
        return [], 10000 # No ride-sharing

    if not set(ass_day_ref) == set(ass_day_ref_prime):  # Different set of assignments, ride-sharing is always impossible
        return [], 10000 # So no ride-sharing

    if len(sol['rs_route'][ref][day_game]) > 0 and len(sol['rs_route'][ref_prime][day_game]) > 0: # Both are ride-sharing already
        return [], 10000 # Do not combine routes at this point

    elif len(sol['rs_route'][ref][day_game]) > 0: # Only ref is involved in ride-sharing already
        print(sol['rs_route'][ref][day_game])
        print(sol['rs_received'][ref][day_game])
        print(sol['rs_given'][ref][day_game])
        raise Exception("Ref is offering ride-sharing, however he can never be offering since his ride-sharing should have"
                        "been removed")
        ref_in_rs = ref
        ref_not_in_rs = ref_prime
        new_dists, poss_routes = loop_distance(ref_in_rs, ref_not_in_rs, day_game, sol, gs)
        idx_insert = [idx for idx in range(len(new_dists)) if new_dists[idx] == min(new_dists)][0] # Insert at index with minimal distance
        best_route = poss_routes[idx_insert]
        dist_no_rs = sol['assignments_base_dist'][best_route[0]][day_game]

        if new_dists[idx_insert] < dist_no_rs * (1 + gs['m']): # Within the allowed range
            return best_route, new_dists[idx_insert]
        else: # Even best option for ride-sharing is impossible
            return [], 10000

    elif len(sol['rs_route'][ref_prime][day_game]) > 0: # Only ref_prime is involved in ride-sharing already

        ref_in_rs = ref_prime
        ref_not_in_rs = ref
        new_dists, poss_routes = loop_distance(ref_in_rs, ref_not_in_rs, day_game, sol, gs)
        idx_insert = [idx for idx in range(len(new_dists)) if new_dists[idx] == min(new_dists)][0]  # Insert at index with minimal distance
        best_route = poss_routes[idx_insert]
        dist_no_rs = sol['assignments_base_dist'][best_route[0]][day_game]

        if new_dists[idx_insert] < dist_no_rs * (1 + gs['m']): # Within the allowed range
            return best_route, new_dists[idx_insert]
        else: # Even best option for ride-sharing is impossible
            return [], 10000



    else: # Neither is involved in ride sharing yet
        route_ref = [ref, ref_prime] + [gs['nrefs'] + game for game in sol['ref_day_assignments'][ref][day_game]] + [ref_prime, ref]
        # Route of ref offering ride-sharing
        route_ref_prime = [ref_prime, ref] + [gs['nrefs'] + game for game in sol['ref_day_assignments'][ref][day_game]] + [ref, ref_prime]
        # Route of ref_prime offering ride-sharing
        if gs['kappa'][ref] != 0: # Ref may offer ride-sharing
            dist_ref = sum([gs['distance_matrix'].iloc[route_ref[i], route_ref[i + 1]] for i in range(len(route_ref) - 1)])
        else:
            dist_ref = 10000

        if gs['kappa'][ref_prime] != 0: # Ref may offer ride-sharing
            dist_ref_prime = sum([gs['distance_matrix'].iloc[route_ref_prime[i], route_ref_prime[i + 1]] for i in range(len(route_ref) - 1)])
        else:
            dist_ref_prime = 10000

        if dist_ref < dist_ref_prime: # Referee ref should offer ridesharing for minimum cost
            route_no_rs = [ref] + [gs['nrefs'] + game for game in sol['ref_day_assignments'][ref][day_game]] + [ref]
            dist_no_rs = sum([gs['distance_matrix'].iloc[route_no_rs[i], route_no_rs[i + 1]] for i in range(len(route_no_rs) - 1)])
            if dist_ref <= (1 + gs['m']) * dist_no_rs: # If distance added is not too high for this referee
                return route_ref, dist_ref
            else:
                return [], 10000
        else: # Referee ref_prime could offer ridesharing for minimum cost
            route_no_rs = [ref_prime] + [gs['nrefs'] + game for game in sol['ref_day_assignments'][ref][day_game]] + [ref_prime]
            dist_no_rs = sum([gs['distance_matrix'].iloc[route_no_rs[i], route_no_rs[i + 1]] for i in range(len(route_no_rs) - 1)])
            if dist_ref_prime <= (1 + gs['m']) * dist_no_rs: # If distance added is not too high for this referee
                return route_ref_prime, dist_ref_prime
            else:
                return [], 10000

def loop_distance(ref_loop, ref_other, day_game, sol, gs):
    '''
    Calculates the distances of inserting ref_other in the route of ref_loop
    '''
    refs_cur = [ref for ref in sol['rs_route'][ref_loop][day_game] if ref < gs['nrefs']]
    nrefs_cur = int(len(refs_cur) / 2)  # Since refs are always present twice

    if abs(nrefs_cur % 1) > 0.01:
        print(f"Error in loop_distance within Rs_possible_distance: number of referees is not an integer number. Instead: "
              f"{nrefs_cur}")
        print(sol['rs_route'][ref_loop][day_game])
        print(sol['assignments_day'][ref_loop][day_game])

    distances = [sol['rs_dist'][ref_loop][day_game] for _ in range(nrefs_cur+1)] # Original distance of route
    cur_route = sol['rs_route'][ref_loop][day_game]
    cur_route_vec = [cur_route.copy() for _ in range(nrefs_cur+1)]
    for idx in range(nrefs_cur+1): # Loop through indices where new ref could be placed
        if idx == 0: # ref_other would be at the start of the route
            if nrefs_cur >= gs['kappa'][ref_other]: # Already at max capacity:
                distances[idx] += 10000 # To ensure it is never possible
            else:
                distances[idx] += 2 * gs['distance_matrix'].iloc[ref_other, cur_route[0]] # Distance of ref to original start point
            cur_route_vec[idx].insert(0, ref_other) # Insert at start of route
            cur_route_vec[idx].insert(len(cur_route) + 1, ref_other) # Insert at end of route
        else: # ref_other would be placed somewhere within the route
            if nrefs_cur >= gs['kappa'][cur_route[0]]: # Already at max capacity:
                distances[idx] += 10000 # To ensure it is never possible
            # Distance of location before and after placement needs to be removed:
            distances[idx] -= gs['distance_matrix'].iloc[cur_route[idx - 1], cur_route[idx]]
            distances[idx] -= gs['distance_matrix'].iloc[cur_route[len(cur_route) - idx - 1], cur_route[len(cur_route) - idx]]
            # Distance of location before to ref needs to be added:
            distances[idx] += gs['distance_matrix'].iloc[cur_route[idx - 1], ref_other]
            distances[idx] += gs['distance_matrix'].iloc[cur_route[len(cur_route) - idx], ref_other]
            # Distance of location after to ref needs to be added:
            distances[idx] += gs['distance_matrix'].iloc[cur_route[idx], ref_other]
            distances[idx] += gs['distance_matrix'].iloc[cur_route[len(cur_route) - idx - 1], ref_other]
            cur_route_vec[idx].insert(idx, ref_other)  # Insert at start of route at idx
            cur_route_vec[idx].insert(len(cur_route) - idx + 1, ref_other)  # Insert at end of route at len - idx

    return distances, cur_route_vec