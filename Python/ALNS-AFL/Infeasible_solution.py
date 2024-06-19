'''
Here we create an initial infeasible solution to the problem 
Infeasible means that it does not meet all assignment constraints, but only the once that are allowed to be violated
are violated (i.e. minimum assignment, overlap (to limited extent) and availability)

Data structure solution (combined in dictionary):
Referee assignments: [ref] list of integer numbers (index not id) indicating at which matches the referees are assigned
Travelled distance: [ref][date] numerical value indicating how much distance ref travelled on average per date
Assignments day: [ref][date] integer number indicating per referee how many assignments he has at each date
Assignments base dist: [ref][date] numerical value indicating the base distance of the travel on this date
                       (i.e. distance without ride-sharing)
Referee day assignments: [ref][day] yields a list of assignments of this referee on this date (sorted on time)
Ride sharing given: [ref][day] integer indicating to which referees ride-sharing is given at this date
Ride sharing received: [ref][game] integers indicating for each game with which referee ride-sharing is done
Ride sharing distance: [ref][date] distance travelled for ref on this date !Actual distance, not incurred distance!
Ride sharing route: [ref][date] list of locations visited in the ride-sharing route
Ride sharing occurences: lists of (ref, day)-tuples in which ride-sharing happens (merely where ride-sharing is given)
Objective value: one numeric value
Game assignment: list of lists of integer numbers indicating which referees are assigned to the game
Number of E licenses: array of integers indicating the number of E licenses per game


Furthermore, some additional ones are introduced specific for the infeasible algorithm, which keep track of violations:
Time window violation: a list of lists of games indicating per referee at which games time window violations occur
Availability violation: a list of lists of games indicating at which games the availability of a referee is ignored
Gamma violation: a list of integer values indicating per referee how much games he needs to officiate additionally to meet his requirement
Fall back violation: a list of integer values indicating per referee how much fall back violations he has
Weekend violation: a list of integer values indicating per referee how much weekend violations he has
Penalty cost: a list of numeric values indicating the penalty cost per referee
Violation pairs: a list of (ref, game)-tuples where violations occur (w.r.t. time window, availability, fall back or weekend)
'''
# year = 2022



def empty_sol_maker(gs, fx, ride_sharing = False):
       import numpy as np

       ## First we initialize sol as empty lists etc.
       # Referee assignments
       ref_assignments = [[] for _ in range(gs['nrefs'])] # Empty lists for every referee

       # Travelled distance is 0 at all dates
       trav_dist = np.array([[float(0) for _ in range(365)] for _ in range(gs['nrefs'])])

       # Assigned games is 0 at all dates
       assignments_day = np.array([[0 for _ in range(365)] for _ in range(gs['nrefs'])])
       assignments_base_dist = np.array([[float(0) for _ in range(365)] for _ in range(gs['nrefs'])])

       # Ref day assignments
       ref_day_assignments = [[[] for _ in range(365)] for _ in range(gs['nrefs'])]

       # Ride sharing initialized at none at all
       rs_given = [[[] for _ in range(365)] for _ in range(gs['nrefs'])]
       rs_received = np.array([[-1 for _ in range(365)] for _ in range(gs['nrefs'])])
       rs_dist = np.array([[float(0) for _ in range(365)] for _ in range(gs['nrefs'])])
       rs_route = [[[] for _ in range(365)] for _ in range(gs['nrefs'])]
       rs_occur = [] # No tuples to begin with

       # Game assignments
       game_assignments = [[] for _ in range(gs['ngames'])]

       # E licenses:
       E_license = np.array([0 for _ in range(gs['ngames'])])

       # time window violation:
       tw_viol = [[] for _ in range(gs['nrefs'])]

       # availability violation:
       avail_viol = [[] for _ in range(gs['nrefs'])]

       # assignment slack:
       gamma_viol = [gs['referee_df'].loc[ref, 'reqgames'] for ref in range(gs['nrefs'] - 1)]
       gamma_viol.append(0) # For hire referee has no assignment slack
       gamma_viol = np.array(gamma_viol)

       # Fall back violation
       fb_viol = 0

       # Weekend violation
       weekend_viol = [0 for _ in range(gs['nrefs'])]

       # penalty cost:
       penalty_cost = np.array([gamma_viol[ref] * gs['penalty_gamma'] for ref in range(gs['nrefs'])])

       # Violation pairs
       violation_pairs = [] # No violation pairs atm

       # Objective value is sum of travelled distances + sum of penalties
       obj_val = sum(penalty_cost)

       sol = {'ref_assignments': ref_assignments,
              'trav_dist': trav_dist,
              'assignments_day': assignments_day,
              'assignments_base_dist': assignments_base_dist,
              'ref_day_assignments': ref_day_assignments,
              'rs_given': rs_given,
              'rs_received': rs_received,
              'rs_dist': rs_dist,
              'rs_route': rs_route,
              'rs_occur': rs_occur,
              'obj_val': obj_val,
              'game_assignments': game_assignments,
              'E_license': E_license,
              'tw_viol': tw_viol,
              'avail_viol': avail_viol,
              'gamma_viol': gamma_viol,
              'fb_viol': fb_viol,
              'weekend_viol': weekend_viol,
              'penalty_cost': penalty_cost,
              'violation_pairs': violation_pairs}
       return sol

def infeasible_solution(year, ride_sharing = False):
       from globals_maker import gs_maker
       gs = gs_maker(year, False)
       from Function_load import function_load
       fx = function_load(feasible=False, ride_sharing=ride_sharing)
       from Functions.Infeasible.Daily_feasibility_model import daily_feasibility
       sol = empty_sol_maker(gs, fx, ride_sharing)

       ## Based on daily feasibility model:
       for d in gs['game_df']['date'].unique(): # Loop through dates
           ref_game_tuples = daily_feasibility(d, sol, gs, fx)
           for tup in ref_game_tuples:
               sol = fx['fix_sol']((tup[0], tup[1]), sol, gs, fx)  # Update solution

       return sol, gs, fx