'''
For a given referee, this function calculates if a new match would yield problems with overlapping games

Options:
violation (T/F): indicates if we want to check allowing violations or not
'''

def overlapping_game(ref, game, sol, gs, fx, violation = False):
    bool_val = False
    assignments = sol['ref_assignments'][ref]
    if len(assignments) > 0:  # Only if he was priorly assigned to a game
        for ass in assignments:
            if violation:
                if not gs['nu_matrix_prime'][game][ass]:  # Means this game will give overlapping problems
                    bool_val = True
                    break  # No point in continuing the loop, we know already we have an overlapping game
            else:
                if not gs['nu_matrix'][game][ass]:  # Means this game will give overlapping problems
                    bool_val = True
                    break  # No point in continuing the loop, we know already we have an overlapping game

    return bool_val