'''
Calculates for a given game which referees would be a feasible addition to the game.
This is based on:
1. Referee is not officating the game yet
2. Referee is available on the day of the game
    - Availability list has a true value
    - Check if other games of the referees are on the same day and could lead to overlaps
    - Check if there are no weekend violations
    - Check if availability is not fall back
3. Referee is in the feasible league set (valid_assignments)
4. After addition of referee, license limits are not violated
5. After addition of referee, white hat requirements are met

'''

def feasible_refs(game, sol, gs, fx):
    refs = [i for i in range(gs['nrefs'])] # In first instance, all refs are possible

    # 1: Remove referees which are already officiating the game (if any)
    if len(sol['game_assignments'][game]) > 0:
        refs = [ref for ref in refs if ref not in sol['game_assignments'][game]]

    # 3: Referee is in the feasible league set (valid_assignments)
    refs = [ref for ref in refs if gs['valid_assignments'][ref][game]]

    # 4: After addition of referee, license limits are not violated
    refs = [ref for ref in refs if sol['E_license'][game] + (gs['referee_df'].loc[ref, 'license'] == 'E') <=
            gs['license_requirements'][game]]

    # 5: After addition of referee, white hat requirements are met
    cur_refs = sol['game_assignments'][game]  # Current assigned refs
    cur_whs = [gs['valid_wh'][ref][game] for ref in cur_refs] # First check if wh requirement is already met
    if sum(cur_whs) < gs['wh_needed'][game]: # If not
        refs = [ref for ref in refs if gs['valid_wh'][ref][game]] # Only keep the valid white hats

    # 2: Remove referees which are not available
    # - Availability indicates as yes
    refs_save = refs.copy() # Make a copy: if no refs possible, we try again but then allow violations
    refs = [ref for ref in refs if gs['availability_matrix'][ref][game]]

    # Check for overlap
    refs = [ref for ref in refs if not fx['overlapping_game'](ref, game, sol, gs, fx)]

    # Check if there are no weekend overlap problems
    refs = [ref for ref in refs if not fx['weekend_overlap'](ref, game, sol, gs, fx) > 0]

    # Check for fall back
    refs = [ref for ref in refs if not gs['fb_list'][ref][game]]

    if len(refs) == 0 or refs[0] == gs['nrefs'] - 1:
        refs = refs_save
        refs = [ref for ref in refs if not fx['overlapping_game'](ref, game, sol, gs, fx, 1/3)] # Now allow tw violation
        refs_save = refs.copy()
        refs = [ref for ref in refs if gs['availability_matrix'][ref][game]]
        if len(refs) == 0 or refs[0] == gs['nrefs'] - 1: # Availability must be violated in this case
            refs = refs_save
        else:
            refs_save = refs.copy()
            refs = [ref for ref in refs if not gs['fb_list'][ref][game]] # Check fall back again
            if len(refs) == 0 or refs[0] == gs['nrefs'] - 1: # Fall back has to be violated
                refs = refs_save
            else:
                refs_save = refs.copy()
                refs = [ref for ref in refs if not fx['weekend_overlap'](ref, game, sol, gs, fx) > 0]
                if len(refs) == 0 or refs[0] == gs['nrefs'] - 1: # Weekend restriction has to be violated
                    refs = refs_save

    # If there are multiple referee, always exclude the for-hire referee as possibility
    if len(refs) > 1:
        refs = [ref for ref in refs if ref != gs['nrefs'] - 1]

    # If no referee is available for the game, insert the referee for hire
    if len(refs) == 0:
        refs = [gs['nrefs'] - 1]
        # raise Exception(f"Crucial error: no feasible assignment to game {game} can be found. Algorithm broke down")

    return refs