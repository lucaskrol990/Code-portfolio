'''
4. Officials may only officiate games within their allowed leagues
- t1 match requires only t1 official
- t2 match requires only t2 official
- leagues not in "own team" require that official is not officiating a match of his/her own team
'''

def feasibility_4(sol, gs, fx):
    n_infeasibilities = 0
    for ref in range(gs['nrefs']):
        ref_ass = sol['ref_assignments'][ref]
        if len(ref_ass) > 0: # If there is an assignment for this referee
            for game in ref_ass:
                if gs['valid_assignments'][ref][game] == 0: # If assignment is not valid
                    print(f"Infeasible: Invalid assignment of referee {ref} to game {game} (w.r.t. league)")
                    n_infeasibilities += 1 # Additional infeasibility
    return n_infeasibilities