'''
16. Objective value is sum of travel distances and penalty costs
'''
import numpy as np

def feasibility_16(sol, gs, fx):
    n_infeasibilities = 0
    obj_val = np.sum(sol['trav_dist'] * sol['assignments_day']) + sum(sol['penalty_cost'])

    if abs(obj_val - sol['obj_val']) > 1:
        print(f"According to sol the objective value equals {sol['obj_val']} but it should be {obj_val}")
    return n_infeasibilities