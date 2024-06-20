'''
Checks if the availability of the referees is adhered to when assigning the referees
Notice: in the infeasibility variant, availability can be ignored without creating infeasibility. Therefore, this function
simply returns 0
'''
def feasibility_1(sol, gs, fx):
    return 0