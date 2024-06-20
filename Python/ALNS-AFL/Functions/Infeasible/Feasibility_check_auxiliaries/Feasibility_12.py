'''
12. Weekend restrictions are met (if availability day = '*', then no assignments to other days with '*' around it)
Infeasible version ==> violations allowed at a cost
'''

def feasibility_12(sol, gs, fx):
    n_infeasibilities = 0
    # for ref in range(gs['nrefs']):
    #     assignments = sol['ref_assignments'][ref] # Assignments of referee
    #     day_assignments = gs['game_df'].loc[assignments, 'date'].tolist() # Days of assignments
    #     for day in day_assignments: # Loop through days of assignments
    #         if len(gs['weekend_list'][ref][day]) > 0: # If there is a restriction on this date
    #             for day_restric in gs['weekend_list'][ref][day]: # Loop through restricted dates
    #                 if day_restric in day_assignments: # If this restricted date is in another assignment
    #                     print(f"Infeasible: Referee {ref} is assigned to a game on day {day} as well as day {day_restric}. "
    #                           f"However the referee was only willing to officiate on one of these days")
    #                     n_infeasibilities += 1

    return n_infeasibilities