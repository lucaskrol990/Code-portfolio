'''
Checks if the number of assignment per referee exceeds the minimum amount required to maintain the license
In the infeasible solution, the minimum number of assignments per referee is soft and therefore we return 0
'''

def feasibility_5(sol, gs, fx):
    n_infeasibilities = 0
    return n_infeasibilities