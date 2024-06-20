'''
6. License class requirements
- If t1/t2 or (Regionalliga and division senior):
    - E = 0
- If cup and # participating teams < 3:
    - E <= 1
- Else:
    - E <= 2
'''

def feasibility_6(sol, gs, fx):
    n_infeasibilities = 0
    for game in range(gs['ngames']): # Loop through games
        if sol['E_license'][game] > gs['license_requirements'][game]:
            print(f"Infeasible: To game {game} a total of {sol['E_license'][game]} refs with an E license were assigned, "
                  f"the maximum was {gs['license_requirements'][game]}")
            n_infeasibilities += 1
    return n_infeasibilities