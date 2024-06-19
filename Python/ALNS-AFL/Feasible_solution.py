from globals_maker import gs_maker
gs = gs_maker(2022, True)
from Function_load import function_load
fx = function_load(True)
from Functions.Feasible.Daily_feasibility_model import daily_feasibility

'''
Here we create an initial feasible solution to the problem 

Data structure solution (combined in dictionary):
1. Referee assignments: list of lists of integer numbers (index not id) at which matches the referees are assigned
2. Travelled distance: list of list of numerical values per referee indicating how much distance he/she travelled 
                       on average per date
3. Assignments day: list of lists of integer number indicating per referee how many assignments he has at each date
4. Ride sharing received: list of lists of (game, integer)-tuples indicating for which game ride sharing with which referee is done
5. Ride sharing given: list of lists of [game, [ride sharing refs]] indicating to which referees ride sharing is offered
6. Objective value: one numeric value
7. Game assignment: list of lists of integer numbers indicating which referees are assigned to the game
8: Number of E licenses: array of integers indicating the number of E licenses per game
'''


## First we initialize sol as empty lists etc.
# 1: Referee assignments
ref_assignments = [[] for _ in range(gs['nrefs'])] # Empty lists for every referee

# 2: Travelled distance is 0 everywhere
trav_dist = [[0 for _ in range(365)] for _ in range(gs['nrefs'])]

# 3: Assigned games is 0 at all dates
assignments_day = [[0 for _ in range(365)] for _ in range(gs['nrefs'])]

# 4+5: Ride sharing initialized at none at all
rs_received = [[] for _ in range(gs['nrefs'])]
rs_given = [[] for _ in range(gs['nrefs'])]

# 6: Objective value is sum of travelled distances
obj_val = sum(trav_dist)

# 7: Game assignments
game_assignments = [[] for _ in range(gs['ngames'])] # Initialize an empty array with length equal to # of games

# 8: E licenses:
E_license = [0 for _ in range(gs['ngames'])]

sol = {'ref_assignments': ref_assignments,
       'trav_dist': trav_dist,
       'assignments_day': assignments_day,
       'rs_received': rs_received,
       'rs_given': rs_given,
       'obj_val': obj_val,
       'game_assignments': game_assignments,
       'E_license': E_license}


## Based on daily feasibility model:
for d in gs['game_df']['date'].unique(): # Loop through dates
    ref_game_tuples = daily_feasibility(d, sol, gs, fx)
    for tup in ref_game_tuples:
        sol = fx['fix_sol']((tup[0], tup[1]), sol, gs, fx)  # Update solution