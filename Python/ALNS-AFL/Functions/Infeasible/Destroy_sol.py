'''
This function destroy the sol variable based on the deletion of ref-game assignments
Input: (ref, game)-tuples (potentially list)
Output: sol (destroyed & infeasible)

Data structure solution (combined in dictionary):
1. Referee assignments: list of lists of integer numbers (index not id) at which matches the referees are assigned
2. Travelled distance: list of numerical values per referee indicating how much distance he/she travelled in total
3. Ride sharing received: list of lists of (game, integer)-tuples indicating for which game ride sharing with which referee is done
4. Ride sharing given: list of lists of [game, [ride sharing refs]] indicating to which referees ride sharing is offered
5. Objective value: one numeric value
6. Game assignment: list of lists of integer numbers indicating which referees are assigned to the game
7: Number of E licenses: array of integers indicating the number of E licenses per game
'''

def destroy_sol(ref_game, sol, gs, fx):
    if type(ref_game) == list: # If list, we need to loop throug the tuples
        for tup in ref_game:
            sol = destroy_sol_single(tup, sol, gs, fx)
    else:
        sol = destroy_sol_single(ref_game, sol, gs, fx)
    return sol

def destroy_sol_single(ref_game, sol, gs, fx):
    ref = ref_game[0]
    game = ref_game[1]

    dist_change = distance_remove(ref, game, sol, gs, fx)
    delta_violation = violation_change(ref, game, sol, gs, fx)
    day_game = gs['game_df'].loc[game, 'date']

    if game in sol['tw_viol'][ref] or gs['fb_list'][ref][game] or not gs['availability_matrix'][ref][game] \
            or ref == gs['nrefs'] - 1: # If there used to be a violation
        if (ref, game) not in sol['violation_pairs']:
            print(game in sol['tw_viol'][ref])
            print(game in sol['fb_viol'][ref])
            print(gs['availability_matrix'][ref][game])
            print(ref == gs['nrefs'] - 1)
            raise Exception("Error because combination is not in sol['violation_pairs']")
        sol['violation_pairs'].remove((ref, game)) # Remove ref-game pair

    sol['ref_assignments'][ref].remove(game) # Remove game from ref
    sol['obj_val'] += dist_change + delta_violation # Update objective value
    # Update travelled distance:
    if sol['assignments_day'][ref][day_game] > 1: # More than one assignment
        # So we update using 'tot distance new' / 'number of assignments new'
        sol['trav_dist'][ref][day_game] = (sol['trav_dist'][ref][day_game] * sol['assignments_day'][ref][day_game]
                                           + dist_change) / (sol['assignments_day'][ref][day_game] - 1)
    else: # Only 1 assignment before, so now 0
        sol['trav_dist'][ref][day_game] = 0

    sol['ref_day_assignments'][ref][day_game].remove(game) # Remove game on this date
    sol['assignments_day'][ref][day_game] -= 1 # Update assignments on this day
    sol['game_assignments'][game].remove(ref) # Remove referee from game
    sol['E_license'][game] -= gs['referee_df'].loc[ref, 'license'] == 'E' # If ref has E license, remove one from game
    sol['penalty_cost'][ref] += delta_violation
    if ref != gs['nrefs'] - 1:  # We ignore violations from the for hire ref
        if game in sol['tw_viol'][ref]: # If there is a tw violation
            sol['tw_viol'][ref].remove(game) # Remove the game
        if not gs['availability_matrix'][ref][game]: # If there was an availability violation
            sol['avail_viol'][ref].remove(game) # Remove the game
        sol['gamma_viol'][ref] += 1 # Game removed, so violation increases by 1
        if gs['fb_list'][ref][game]: # If fb assignment game removed
            sol['fb_viol'] -= 1 # Remove from counter
        sol['weekend_viol'][ref] -= fx['weekend_overlap'](ref, game, sol, gs, fx)  # If this removes weekend overlap, remove values


    ##! Ride sharings fixings ignored!
    return sol

def distance_remove(ref, game, sol, gs, fx):
    '''
    This function calculates the total distance which can be removed due to the removal of a game from a referee
    It starts with removing distances due to violations
    Then it looks at the actual distances
    '''
    dist_change = 0
    if ref == gs['nrefs'] - 1:  # If hired ref
        return dist_change


    date_assignment = gs['game_df'].loc[game, 'date']
    duplicate_ass = [ass for ass in sol['ref_day_assignments'][ref][date_assignment] if ass != game]
    if len(duplicate_ass) == 0:
        # No same day assignments -> remove twice the distance from game to referee
        dist_change = -2 * gs['distance_matrix'].iloc[ref, gs['nrefs'] + game]
    else:
        # More assignments at one day -> check which ones before and which ones after
        ass_before = [ass for ass in duplicate_ass if gs['game_df'].loc[ass, 'time'] <= gs['game_df'].loc[game, 'time']]
        ass_after = [ass for ass in duplicate_ass if gs['game_df'].loc[ass, 'time'] >= gs['game_df'].loc[game, 'time']]

        if len(ass_before) == 0: # If nothing before
            start_loc = ref # Started at referee location
        else: # If was something before
            start_loc = gs['nrefs'] + gs['game_df'].loc[ass_before, 'time'].idxmax() # Started at this game

        if len(ass_after) == 0: # If nothing after
            end_loc = ref # Ended at referee location
        else: # If was something after
            end_loc = gs['nrefs'] + gs['game_df'].loc[ass_after, 'time'].idxmin() # Ended at this game

        dist_change -= gs['distance_matrix'].iloc[start_loc, gs['nrefs'] + game] # This is now removed
        dist_change -= gs['distance_matrix'].iloc[gs['nrefs'] + game, end_loc] # This is now removed
        dist_change += gs['distance_matrix'].iloc[start_loc, end_loc] # Route has to be fixed again
    return dist_change

def violation_change(ref, game, sol, gs, fx):
    viol_change = 0
    if ref == gs['nrefs'] - 1:  # If hired ref
        viol_change -= gs['penalty_hire'] # One less penalty for that now
        return viol_change

    if game in sol['tw_viol'][ref]:  # If there was a time window violation
        viol_change -= gs['penalty_tw']  # We can remove penalty of time window

    if not gs['availability_matrix'][ref][game]:  # If the referee was not availabile
        viol_change -= gs['penalty_avail']  # Remove penalty of availability violation

    if sol['gamma_viol'][ref] >= 0:  # If there will be an availability violation at this point
        viol_change += gs['penalty_gamma']  # There is one more violation now, so increase the violation

    if sol['fb_viol'] > gs['max_fb']: # If the total amount of fb violations exceeded the maximum before
        viol_change -= gs['penalty_fb'] * gs['fb_list'][ref][game] # If we now have one less, remove penalty

    if fx['weekend_overlap'](ref, game, sol, gs, fx) > 0: # If there used to be weekend overlap
        viol_change -= fx['weekend_overlap'](ref, game, sol, gs, fx) * gs['penalty_weekend'] # One times weekend overlap less

    return viol_change




