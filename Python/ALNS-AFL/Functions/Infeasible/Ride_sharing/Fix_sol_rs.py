'''
This function fixes the sol variable based on new ref-game assignments
Input: (ref, game)-tuples (potentially list
Output: sol (fixed & feasible)

We have to adhere to the following sequence when fixing the solution:
1. Calculate the violation change (which is based on not having the solution fixed already)
2. Change the assignments
3. Remove current ride-sharings, if any
4. Recalculate base_dist since it is used in rs_possible_distance
5. Look for new ride-sharings using rs_possible_dist and recalculate the distances
'''

def fix_sol(ref_game, sol, gs, fx):
    if type(ref_game) == list:  # If list, we need to loop throug the tuples
        for tup in ref_game:
            sol = fix_sol_single(tup, sol, gs, fx)
    else:
        sol = fix_sol_single(ref_game, sol, gs, fx)
    return sol


def fix_sol_single(ref_game, sol, gs, fx):
    ref = ref_game[0]
    game = ref_game[1]
    day_game = gs['game_df'].loc[game, 'date']

    # First we check if a new time window violation occurs with our ref-game assignment
    if fx['overlapping_game'](ref, game, sol, gs, fx, violation=True):
        tw_viol = True
    else:
        tw_viol = False

    delta_violation = violation_change(ref, game, sol, gs, fx, tw_viol)


    if tw_viol or gs['fb_list'][ref][game] or not gs['availability_matrix'][ref][game] \
            or ref == gs['nrefs'] - 1:  # If violation added
        sol['violation_pairs'].append((ref, game))  # Add ref-game pair

    sol['ref_assignments'][ref].append(game)  # Assign game to ref
    sol['ref_day_assignments'][ref][day_game] = sorted(sol['ref_day_assignments'][ref][day_game] + [game])
    sol['assignments_day'][ref][day_game] += 1  # Update assignments on this day
    sol['game_assignments'][game].append(ref)  # Assign referee to game
    sol['E_license'][game] += gs['referee_df'].loc[ref, 'license'] == 'E'  # If ref has E license, add one to game
    sol['penalty_cost'][ref] += delta_violation
    if ref != gs['nrefs'] - 1:  # We ignore violations from the for hire ref
        if tw_viol:  # If there is a tw violation
            sol['tw_viol'][ref].append(game)  # Add the game
        if not gs['availability_matrix'][ref][game]:  # If there is an availability violation
            sol['avail_viol'][ref].append(game)  # Add the game
        #if sol['gamma_viol'][ref] > 0:
        sol['gamma_viol'][ref] -= 1  # Game assigned, so violation decreases by 1
        if gs['fb_list'][ref][game]:  # If fb assignment game added
            sol['fb_viol'] += 1  # Add to counter
        sol['weekend_viol'][ref] += fx['weekend_overlap'](ref, game, sol, gs,
                                                          fx)  # If this adds weekend overlap, add it

    ## Updating of the ride-sharing variables
    delta_dist = 0
    # If the ref offered ride-sharing before, the ref now needs to delete old values
    if len(sol['rs_given'][ref][day_game]) > 0:
        sol, delta_dist = rs_given_remove(ref, day_game, sol, gs, fx, delta_dist)

    # If ref received ride-sharing before, this now has to be removed:
    if sol['rs_received'][ref][day_game] != -1:
        sol, delta_dist = rs_received_remove(ref, day_game, sol, gs, fx, delta_dist)

    # Updating of distances
    dist_change = distance_fix(ref, game, sol, gs, fx)
    sol['assignments_base_dist'][ref][day_game] += dist_change  # Base distance always goes up with dist_change



    # Then we calculate if ride-sharing is possible in this new solution
    routes = []
    dists = []
    ref_ignore = [ref] # Referees we can ignore (because we have calculated the best insertion already or it is ref self)
    for ref_prime in sol['game_assignments'][game]:
        if ref_prime not in ref_ignore:
            tmp = fx['rs_possible_distance'](ref, ref_prime, game, sol, gs, fx)
            ref_ignore.extend([loc for loc in sol['rs_route'][ref_prime][day_game] if loc < gs['nrefs']]) # Ignore ones with the same route
            routes.append(tmp[0])
            dists.append(tmp[1])


    # Check if new ride-sharing can happen
    if len(dists) > 0:  # If no other refs for the game, no point in checking refs
        if min(dists) == 10000:  # Dist = 10000 ==> Ride sharing not possible
            pass  # No changes to ride-sharing variables have to be made
        else: # Ride-sharing will happen
            best_idx = [idx for idx in range(len(dists)) if dists[idx] == min(dists)][0]  # Go for the one with minimal distance
            ref_giving_rs = routes[best_idx][0]
            if ref_giving_rs == ref: # This referee is at the start of ride-sharing route
                sol, delta_dist = referee_offering_rs(routes, dists, best_idx, ref, day_game, sol, gs, fx, delta_dist)
            else: # Other referee at start of ride-sharing
                sol, delta_dist = other_ref_offering_rs(dists, routes, best_idx, ref, ref_giving_rs, day_game, sol, gs, fx, delta_dist)




    there_was_rs = False
    if len(dists) > 0:
        if min(dists) != 10000: # There was ride-sharing before, all updates have happened already
            there_was_rs = True

    if not there_was_rs: # There was no ride-sharing, so only update distance of this ref
        delta_dist += dist_change
        sol['trav_dist'][ref][day_game] = sol['assignments_base_dist'][ref][day_game] / sol['assignments_day'][ref][day_game]

    sol['obj_val'] += delta_dist + delta_violation  # Update objective value
    return sol


def distance_fix(ref, game, sol, gs, fx):
    day_assignment = gs['game_df'].loc[game, 'date']
    dist_change = 0
    if ref == gs['nrefs'] - 1:  # If hired ref
        return 0

    duplicate_assignments = [ass for ass in sol['ref_day_assignments'][ref][day_assignment] if ass != game]
    if len(duplicate_assignments) == 0:  # First assignment on this day
        # Just need to add distance of referee to game and back
        dist_change += 2 * fx['distance_calculation'](ref, ref, gs['nrefs'] + game, sol, gs)
    else:  # Multiple assignments on day
        # First check if assignments are before or after (or both)
        times_assignments = []
        for i in duplicate_assignments:
            times_assignments.append(gs['game_df'].loc[i, 'time'])
        game_time = gs['game_df'].loc[game, 'time']
        before_assignment = [i for i in duplicate_assignments if gs['game_df'].loc[i, 'time'] <= game_time]
        after_assignment = [i for i in duplicate_assignments if gs['game_df'].loc[i, 'time'] >= game_time]

        # Find start location of referee
        if len(before_assignment) > 0:
            # Find index of max time before this game and add to nrefs to obtain start location of travel
            start_loc = gs['nrefs'] + gs['game_df'].loc[before_assignment, 'time'].idxmax()  # Started at this game
        else:
            start_loc = ref  # Else starts from referee location

        if len(after_assignment) > 0:
            # Find index of min time after this game and add to nrefs to obtain next location of travel
            end_loc = gs['nrefs'] + gs['game_df'].loc[after_assignment, 'time'].idxmin()
        else:
            end_loc = ref  # Else goes back to referee location

        dist_change -= fx['distance_calculation'](ref, start_loc, end_loc, sol,
                                                  gs)  # Remove distance which was travelled before
        dist_change += fx['distance_calculation'](ref, start_loc, gs['nrefs'] + game, sol,
                                                  gs)  # Add distances travelled now
        dist_change += fx['distance_calculation'](ref, gs['nrefs'] + game, end_loc, sol,
                                                  gs)  # Add distances travelled now
    return dist_change


def violation_change(ref, game, sol, gs, fx, tw_viol):
    viol_change = 0
    if ref == gs['nrefs'] - 1:  # If hired ref
        viol_change += gs['penalty_hire']
        return viol_change

    if tw_viol:  # If there is a time window violation
        viol_change += gs['penalty_tw']  # Add penalty of time window as well as regular distance

    if not gs['availability_matrix'][ref][game]:  # If the referee was not availabile
        viol_change += gs['penalty_avail']  # Add penalty of availability violation as well as regular distance

    if sol['gamma_viol'][ref] > 0:  # If there was a minimum assignment violation at this point
        viol_change -= gs['penalty_gamma']  # There is one less violation now, so reduce the distance!

    if sol['fb_viol'] >= gs['max_fb']:  # If we are at, or over, the edge of having a fb violation before
        viol_change += gs['penalty_fb'] * gs['fb_list'][ref][game]  # If we now have one more, add penalty

    if fx['weekend_overlap'](ref, game, sol, gs, fx) > 0:  # If there now is weekend overlap
        viol_change += fx['weekend_overlap'](ref, game, sol, gs, fx) * gs['penalty_weekend']  # Add the penalty

    return viol_change


def rs_given_remove(ref, day_game, sol, gs, fx, delta_dist):
    '''
    If ref is giving ride-sharing on day_game, this function updates sol accordingly
    '''
    for ref_prime in sol['rs_given'][ref][day_game]:
        sol['rs_received'][ref_prime][day_game] = -1  # Removes ride-sharing for all other refs
        sol['rs_route'][ref_prime][day_game] = []  # Set route to empty for all refs now
        delta_dist += sol['assignments_base_dist'][ref_prime][day_game]  # These refs now will incur base distance
        sol['trav_dist'][ref_prime][day_game] = sol['assignments_base_dist'][ref_prime][day_game] / \
                                                sol['assignments_day'][ref_prime][day_game]  # Also update trav_dist
        sol['rs_dist'][ref_prime][day_game] = 0  # Distance now updated for all refs

    sol['rs_given'][ref][day_game] = []  # No ride-sharing offered anymore by this ref now
    sol['rs_route'][ref][day_game] = [] # No route anymore
    delta_dist += sol['assignments_base_dist'][ref][day_game] - sol['rs_dist'][ref][day_game]
    sol['rs_dist'][ref][day_game] = 0 # No distance anymore
    if sol['assignments_day'][ref][day_game] > 1:
        sol['trav_dist'][ref][day_game] = sol['assignments_base_dist'][ref][day_game] / (sol['assignments_day'][ref][day_game]-1)
    else:
        sol['trav_dist'][ref][day_game] = 0
    return sol, delta_dist

def rs_received_remove(ref, day_game, sol, gs, fx, delta_dist):
    '''
    If ref is receiving ride-sharing on day_game, this function updates sol accordingly
    '''
    ref_giving_rs = sol['rs_received'][ref][day_game]
    sol['rs_received'][ref][day_game] = -1  # Change to not receiving ride-sharing for this day

    ## Update for other refs are needed
    if len(sol['rs_given'][ref_giving_rs][day_game]) == 1: # You are the only one receiving ride-sharing, so destroy fully
        new_route = []
        dist_change_rs = -sol['rs_dist'][ref_giving_rs][day_game]
        delta_dist += sol['assignments_base_dist'][ref_giving_rs][day_game] - sol['rs_dist'][ref_giving_rs][day_game]
        # Update delta_dist here already as it is more convenient
    else:
        # We need to remove the edges connected to ref:
        locs_remove = [sol['rs_route'][ref][day_game][i] for i in range(1, len(sol['rs_route'][ref][day_game]))
                       if sol['rs_route'][ref][day_game][i - 1] == ref]
        locs_remove.extend([sol['rs_route'][ref][day_game][i] for i in range(0, len(sol['rs_route'][ref][day_game]) - 1)
                            if sol['rs_route'][ref][day_game][i + 1] == ref])

        dist_change_rs = -sum([gs['distance_matrix'].iloc[ref, loc] for loc in locs_remove])  # Remove edges from sol
        dist_change_rs += (gs['distance_matrix'].iloc[locs_remove[0], locs_remove[1]] +
                           gs['distance_matrix'].iloc[locs_remove[2], locs_remove[3]])  # Fix route again
        new_route = [loc for loc in sol['rs_route'][ref][day_game] if loc != ref]  # Remove ref from route

    for ref_prime in sol['rs_given'][ref_giving_rs][day_game]:
        sol['rs_route'][ref_prime][day_game] = new_route  # Add this route to all refs now
        sol['rs_dist'][ref_prime][day_game] += dist_change_rs  # Distance now updated for all refs

    # Update stats of ride-sharing offerer
    sol['rs_given'][ref_giving_rs][day_game].remove(ref)  # This ref_rs is now not giving rs to ref anymore
    sol['rs_route'][ref_giving_rs][day_game] = new_route  # Ref_rs itself also needs updated route
    sol['rs_dist'][ref_giving_rs][day_game] += dist_change_rs  # Ref_rs itself also needs updated distances
    if len(new_route) > 0: # If there is still ride-sharing happening
        sol['trav_dist'][ref_giving_rs][day_game] = sol['rs_dist'][ref_giving_rs][day_game] / \
                                                sol['assignments_day'][ref_giving_rs][day_game] # Update trav dist as well
        delta_dist += dist_change_rs  # Less distance travelled now for ref_rs
    else:
        # Notice that delta_dist was updated already before in this case
        sol['trav_dist'][ref_giving_rs][day_game] = sol['assignments_base_dist'][ref_giving_rs][day_game] / \
                                                    sol['assignments_day'][ref_giving_rs][day_game]

    ## Update stats for this ref as well
    sol['rs_dist'][ref][day_game] = 0  # No ride-sharing distance anymore
    sol['rs_route'][ref][day_game] = []  # Empty ride-sharing route now
    delta_dist += sol['assignments_base_dist'][ref][day_game] # Now actual distance is incurred again instead of ride-sharing distance
    sol['trav_dist'][ref][day_game] = sol['assignments_base_dist'][ref][day_game] / (sol['assignments_day'][ref][day_game] - 1)
    # Make sure that this is also updated in trav_dist
    return sol, delta_dist


def referee_offering_rs(routes, dists, best_idx, ref, day_game, sol, gs, fx, delta_dist):
    '''
    If ref is offering ride-sharing on day_game now, we updated sol with this function
    '''
    refs_in_route = [loc for loc in routes[best_idx] if loc < gs['nrefs']]  # Refs in route
    refs_in_route_unique = [refs_in_route[i] for i in range(len(refs_in_route)) if
                            refs_in_route[i] not in refs_in_route[:i]]

    if len(refs_in_route_unique) == 2:  # Only one other ref in ride-sharing, so there was no prior ride-sharing going on
        pass  # Nothing special needs to happen
    else:  # More refs ==> prior ride-sharing ==> these stats need to be removed
        previous_rs_ref = refs_in_route_unique[1]  # Ref previously offering ride-sharing
        if len(sol['rs_given'][previous_rs_ref][day_game]) == 0:
            print('-*' * 50)
            print("Error printing starts here")
            for ref_prime in refs_in_route_unique:
                print(ref_prime)
                print(sol['rs_given'][ref_prime][day_game])
            raise Exception("Wrong ride sharing offerer found in Fix_sol_rs")
        sol, delta_dist = rs_given_remove(previous_rs_ref, day_game, sol, gs, fx, delta_dist)

    sol['rs_given'][ref][day_game].extend(refs_in_route_unique[1:])  # We add the other refs as given a ride-share

    for ref_prime in refs_in_route_unique:
        if ref_prime != ref:  # This ref is receiving not giving
            if sol['rs_received'][ref_prime][day_game] == -1:  # If other ref did not receive before
                delta_dist -= sol['assignments_base_dist'][ref_prime][day_game]  # Base distance is removed
                sol['trav_dist'][ref_prime][day_game] = 0 # Distance is now 0 for this ref_prime
            sol['rs_received'][ref_prime][day_game] = ref  # Adds ride-sharing for all other refs
        sol['rs_route'][ref_prime][day_game] = routes[best_idx]  # Add this route to all refs now
        sol['rs_dist'][ref_prime][day_game] = dists[best_idx]  # Distance now updated for all refs

    # Update distances
    delta_dist += dists[best_idx] - sol['trav_dist'][ref][day_game] * (sol['assignments_day'][ref][day_game] - 1)
    sol['trav_dist'][ref][day_game] = dists[best_idx] / sol['assignments_day'][ref][day_game]

    return sol, delta_dist

def other_ref_offering_rs(dists, routes, best_idx, ref, ref_giving_rs, day_game, sol, gs, fx, delta_dist):
    '''
    If other ref than ref is offering ride-sharing on day_game now, we updated sol with this function
    '''
    sol['rs_given'][ref_giving_rs][day_game].append(ref)  # This ref_rs is now also giving rs to ref
    sol['rs_received'][ref][day_game] = ref_giving_rs  # This ref has now ride-sharing received for this date
    delta_dist -= sol['trav_dist'][ref][day_game] * (sol['assignments_day'][ref][day_game] - 1)
    sol['trav_dist'][ref][day_game] = 0 # Our ref now received ride-sharing and doesn't have a travel distance anymore

    for ref_prime in sol['rs_given'][ref_giving_rs][day_game]:
        sol['rs_route'][ref_prime][day_game] = routes[best_idx]  # Add this route to all refs now
        sol['rs_dist'][ref_prime][day_game] = dists[best_idx]  # Distance now updated for all refs

    sol['rs_route'][ref_giving_rs][day_game] = routes[best_idx]  # Ref itself also needs updated route
    delta_dist += dists[best_idx] - sol['trav_dist'][ref_giving_rs][day_game] * sol['assignments_day'][ref_giving_rs][day_game]
    sol['rs_dist'][ref_giving_rs][day_game] = dists[best_idx]  # Ref itself also needs updated distances

    # Update distances
    sol['trav_dist'][ref_giving_rs][day_game] = dists[best_idx] / sol['assignments_day'][ref_giving_rs][day_game]

    return sol, delta_dist


