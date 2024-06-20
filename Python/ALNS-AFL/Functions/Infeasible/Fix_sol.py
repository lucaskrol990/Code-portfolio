'''
This function fixes the sol variable based on new ref-game assignments
Input: (ref, game)-tuples (potentially list
Output: sol (fixed & feasible)

Data structure solution (combined in dictionary):
1. Referee assignments: list of lists of integer numbers (index not id) at which matches the referees are assigned
2. Travelled distance: list of numerical values per referee indicating how much distance he/she travelled in total
3. Ride sharing received: list of lists of (game, integer)-tuples indicating for which game ride sharing with which referee is done
4. Ride sharing given: list of lists of [game, [ride sharing refs]] indicating to which referees ride sharing is offered
5. Objective value: one numeric value
6. Game assignment: list of lists of integer numbers indicating which referees are assigned to the game
7: Number of E licenses: array of integers indicating the number of E licenses per game
'''

def fix_sol(ref_game, sol, gs, fx):
    if type(ref_game) == list: # If list, we need to loop throug the tuples
        for tup in ref_game:
            sol = fix_sol_single(tup, sol, gs, fx)
    else:
        sol = fix_sol_single(ref_game, sol, gs, fx)
    return sol

def fix_sol_single(ref_game, sol, gs, fx):
    ref = ref_game[0]
    game = ref_game[1]

    # First we check if a new time window violation occurs with our ref-game assignment
    if fx['overlapping_game'](ref, game, sol, gs, fx, violation = True):
        tw_viol = True
    else:
        tw_viol = False

    # Starting with distance calculation is more convenient (because of duplicate day check)
    dist_change = distance_fix(ref, game, sol, gs, fx)
    delta_violation = violation_change(ref, game, sol, gs, fx, tw_viol)
    day_game = gs['game_df'].loc[game, 'date']

    if tw_viol or gs['fb_list'][ref][game] or not gs['availability_matrix'][ref][game] \
            or ref == gs['nrefs'] - 1: # If violation added
        sol['violation_pairs'].append((ref, game))  # Add ref-game pair

    sol['ref_assignments'][ref].append(game)  # Assign game to ref
    sol['obj_val'] += dist_change + delta_violation # Update objective value
    if sol['assignments_day'][ref][day_game] == 0: # If no prior assignments on this day
        sol['trav_dist'][ref][day_game] = dist_change # Trav dist is just distance change
    else: # There were prior assignments
        # So we update using 'tot distance old + change' / 'number of assignments new'
        sol['trav_dist'][ref][day_game] = (sol['trav_dist'][ref][day_game] * sol['assignments_day'][ref][day_game]
                                           + dist_change) / (sol['assignments_day'][ref][day_game] + 1)

    sol['ref_day_assignments'][ref][day_game] = sorted(sol['ref_day_assignments'][ref][day_game] + [game])
    sol['assignments_day'][ref][day_game] += 1  # Update assignments on this day
    sol['game_assignments'][game].append(ref) # Assign referee to game
    sol['E_license'][game] += gs['referee_df'].loc[ref, 'license'] == 'E' # If ref has E license, add one to game
    sol['penalty_cost'][ref] += delta_violation
    if ref != gs['nrefs'] - 1: # We ignore violations from the for hire ref
        if tw_viol: # If there is a tw violation
            sol['tw_viol'][ref].append(game) # Add the game
        if not gs['availability_matrix'][ref][game]: # If there is an availability violation
            sol['avail_viol'][ref].append(game) # Add the game
        sol['gamma_viol'][ref] -= 1 # Game assigned, so violation decreases by 1
        if gs['fb_list'][ref][game]: # If fb assignment game added
            sol['fb_viol'] += 1 # Add to list
        sol['weekend_viol'][ref] += fx['weekend_overlap'](ref, game, sol, gs, fx) # If this adds weekend overlap, add it

    ##! Ride sharings fixings ignored!
    return sol


def distance_fix(ref, game, sol, gs, fx):
    day_assignment = gs['game_df'].loc[game, 'date']
    dist_change = 0
    if ref == gs['nrefs'] - 1: # If hired ref
        return 0

    other_assignments = sol['ref_assignments'][ref]
    duplicate_assignments = sol['ref_day_assignments'][ref][day_assignment]
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
            start_loc = gs['nrefs'] + gs['game_df'].loc[before_assignment, 'time'].idxmax() # Started at this game
        else:
            start_loc = ref  # Else starts from referee location

        if len(after_assignment) > 0:
            # Find index of min time after this game and add to nrefs to obtain next location of travel
            end_loc = gs['nrefs'] + gs['game_df'].loc[after_assignment, 'time'].idxmin()
        else:
            end_loc = ref  # Else goes back to referee location

        dist_change -= fx['distance_calculation'](ref, start_loc, end_loc, sol, gs) # Remove distance which was travelled before
        dist_change += fx['distance_calculation'](ref, start_loc, gs['nrefs'] + game, sol, gs) # Add distances travelled now
        dist_change += fx['distance_calculation'](ref, gs['nrefs'] + game, end_loc, sol, gs)  # Add distances travelled now
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

    if sol['gamma_viol'][ref] > 0:  # If there was an availability violation at this point
        viol_change -= gs['penalty_gamma']  # There is one less violation now, so reduce the distance!

    if sol['fb_viol'] >= gs['max_fb']: # If we are at, or over, the edge of having a fb violation before
        viol_change += gs['penalty_fb'] * gs['fb_list'][ref][game] # If we now have one more, add penalty

    if fx['weekend_overlap'](ref, game, sol, gs, fx) > 0: # If there now is weekend overlap
        viol_change += fx['weekend_overlap'](ref, game, sol, gs, fx) * gs['penalty_weekend'] # Add the penalty

    return viol_change

