'''
13. No negative weekend restrictions
'''

def feasibility_13(sol, gs, fx):
    n_infeasibilities = len([i for i in sol['weekend_viol'] if i < 0])
    if n_infeasibilities > 0:
        print(f"Weekend restriction was negative {n_infeasibilities} times")
    return n_infeasibilities