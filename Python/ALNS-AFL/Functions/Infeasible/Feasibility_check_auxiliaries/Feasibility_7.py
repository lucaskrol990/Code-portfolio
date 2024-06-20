'''
7. White hat requirements
- t1 match requires at least one t1+wh official
- t2 match requires at least one t2+wh official
- whp match requires at least one wh official
- match (not t1/t2/whp) requires at least one wh/whp official
- cup match with more than 3 teams requires at least two wh/whp officials
'''

def feasibility_7(sol, gs, fx):
    n_infeasibilities = 0
    for game in range(gs['ngames']):
        assigned_refs = sol['game_assignments'][game]
        wh_refs = sum([gs['valid_assignments'][i][game] for i in assigned_refs])
        if wh_refs < gs['wh_needed'][game]:
            print(f"To game {game} a total of {wh_refs} white hat (prospect) referees were assigned, but at least"
                  f" {gs['wh_needed'][game]} was/were needed")
            n_infeasibilities += 1
    return n_infeasibilities