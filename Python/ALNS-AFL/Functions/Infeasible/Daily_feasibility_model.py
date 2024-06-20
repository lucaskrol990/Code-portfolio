'''
This file runs a model for a given day and calculates a feasible assignment of referees aiming to increase the number of
assignments for referees with few assignments
'''

from gurobipy import Model, GRB, quicksum
from itertools import product


def daily_feasibility(day, sol, gs, fx):
    m = Model("Daily feasibility")
    m.setParam('OutputFlag', 0)
    nrefs = gs['nrefs'] - 1 # Remove hire referee as option
    refs = [i for i in range(nrefs)]
    games = [game for game in range(gs['ngames']) if gs['game_df']['date'][game] == day]
    ngames = len(games)

    labda = [len(ref_ass) for ref_ass in sol['ref_assignments']] # Current assignments
    Gamma = [gamma for gamma in gs['referee_df']['reqgames']] # Minimum assignments
    nu = gs['overlap_matrix'][day]
    nu_prime = gs['overlap_matrix_violation'][day]
    b = [[gs['availability_matrix'][ref][g] for g in games]
         for ref in range(nrefs)]
    league = [[gs['valid_assignments'][ref][g] for g in games] for ref in range(nrefs)]
    k = [gs['wh_needed'][g] for g in games]# Minimum number of white hats
    mu_max = [gs['license_requirements'][g] for g in games] # Maximum number of E referees
    sigma = [gs['game_df']['Number of referees'][g] for g in games] # Number of referees required

    d_prohibited = []
    for ref in range(nrefs):
        disallowed_days = gs['weekend_list'][ref][day]
        for day_restric in disallowed_days:
            if sol['assignments_day'][ref][day_restric] > 0: # Already assigned at a restricted day
                d_prohibited.append(1) # Append 1
                break
        if len(d_prohibited) <= ref: # No disallowement found
            d_prohibited.append(0) # Append 0

    z = m.addVars(refs, vtype=GRB.INTEGER, name="z")  # Assignment mismatch
    x = m.addVars(product(refs, range(ngames)), vtype=GRB.BINARY, name="x")  # Assignments

    s1 = m.addVars(product(refs, range(ngames)), vtype=GRB.CONTINUOUS, name="s1") # Slack on overlap
    s2 = m.addVars(product(refs, range(ngames)), vtype=GRB.CONTINUOUS, name="s2") # Slack on availability
    s3 = m.addVars(range(ngames), vtype=GRB.CONTINUOUS, name="s3") # Slack indicating for hire referee
    s4 = m.addVars(product(refs, range(ngames)), vtype=GRB.CONTINUOUS, name="s4") # Slack indicating fall back
    s5 = m.addVars(product(refs, range(ngames)), vtype=GRB.CONTINUOUS, name="s5")  # Slack indicating weekend violation

    # Constraint 1
    m.addConstrs(z[o] >= Gamma[o] - (labda[o] + quicksum(x[o, g] for g in range(ngames))) for o in refs)

    # Constraint 2:
    m.addConstrs(x[o, g] <= 1 - (1 / ngames) * quicksum((1 - nu_prime[g][g_prime]) * (x[o, g_prime] - s1[o, g_prime])
                                                for g_prime in [i for i in range(ngames)])
                 for g in range(ngames) for o in refs)
    # Constraint 3:
    m.addConstrs(x[o, g] <= 1 - (1 / ngames) * quicksum((1 - nu[g][g_prime]) * x[o, g_prime]
                                                        for g_prime in [i for i in range(ngames)])
                 for g in range(ngames) for o in refs)
    # Constraint 4:
    m.addConstrs(x[o, g] <= b[o][g] + s2[o, g] for g in range(ngames) for o in refs)
    # Constraint 5:
    m.addConstrs(x[o, g] <= league[o][g] for g in range(ngames) for o in refs)
    # Constraint added (one day of the weekend):
    m.addConstrs(x[o, g] == 0 + s5[o, g] for o in refs for g in range(ngames) if d_prohibited[o] == 1)
    # m.addConstrs(x[o, g] == 0 for o in refs for g in range(ngames) if d_prohibited[o] == 1)

    # Constraint added (fall back assignments)
    m.addConstrs(x[o, g] == 0 + s4[o, g] for o in refs for g in range(ngames) if gs['fb_list'][o][g])

    # Constraint 6:
    m.addConstrs(quicksum(x[o, g] for o in refs if gs['valid_wh'][o][g]) >= k[g] for g in range(ngames))

    # Constraint 8:
    m.addConstrs(quicksum(x[o, g] for o in refs if gs['referee_df'].loc[o, 'license'] == 'E') <=
                 mu_max[g] for g in range(ngames))
    # Constraint 9:
    m.addConstrs(quicksum(x[o, g] for o in refs) == sigma[g] - s3[g] for g in range(ngames))

    # Objective function
    w1 = 50
    w2 = 100
    w4 = w2 / 2
    w5 = w4
    w3 = 10000
    m.setObjective(quicksum(z[o] + quicksum(w1 * s1[o, g] + w2 * s2[o, g] + w4 * s4[o, g] + w5 * s5[o, g] for g in range(ngames))
                            for o in range(nrefs)) +
                   quicksum(w3 * s3[g] for g in range(ngames)))
    m.optimize()

    if m.status == GRB.INFEASIBLE:
        print(f"No feasible assignment found for date {day}")
        m.computeIIS()
        m.write("my_ISS.ilp")
        # print("These were the assignment limitations:")
        # print(b)
        return [(0, games[g]) for g in range(ngames) for _ in range(sigma[g])]

    # Find the ref_game assignments
    ref_game = []
    for game in range(ngames):
        game_ass = []
        for ref in refs:
            if x[ref, game].X > 0.5: # If this was an assignment
                game_ass.append((ref, games[game])) # Make it a tuple
        if len(game_ass) != sigma[game]:
            # print(f"No feasible assignment found for date {day}")
            # print(game_ass)
            # print(sigma[game])
            # print(s3[game].X)
            for i in range(int(round(s3[game].X))):
                # print(f"Appending {(nrefs, games[game])}")
                game_ass.append((nrefs, games[game])) # Make it the hired referee
        ref_game.extend(game_ass)

    return ref_game

