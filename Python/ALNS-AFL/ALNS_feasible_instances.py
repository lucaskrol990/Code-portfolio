'''
This function contains the body of the ALNS algorithm. It loads a solution to the problem and improves upon this
with the operators.

Options:
Feasible (T/F): indicates if the feasible or infeasible version of the algorithm should be run
Ride-sharing (T/F): indicates if the ALNS should allow ride-sharing or not
Improve_rs (T/F): indicates if you want to improve the best found solution by looking at ride-sharings
                  Note: only applicable if Ride-sharing == False
'''
inst = 5

Feasible = False
Ride_sharing = True
Improve_rs = True

import pandas as pd
import time
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def empty_sol_maker(gs):
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

def infeasible_solution(ride_sharing = False):
       from globals_maker_feasible_instances import gs_maker
       gs = gs_maker(inst)
       from Function_load import function_load
       fx = function_load(feasible=False, ride_sharing=ride_sharing)
       from Functions.Infeasible.Daily_feasibility_model import daily_feasibility
       sol = empty_sol_maker(gs)

       ## Based on daily feasibility model:
       for d in gs['game_df']['date'].unique(): # Loop through dates
           ref_game_tuples = daily_feasibility(d, sol, gs, fx)
           for tup in ref_game_tuples:
               sol = fx['fix_sol']((tup[0], tup[1]), sol, gs, fx)  # Update solution

       return sol, gs, fx

sol, gs, fx = infeasible_solution(ride_sharing=Ride_sharing)

if Ride_sharing:
    print("With ride-sharing")
elif Improve_rs:
    print("With ride-sharing calculated sequentially")
else:
    print("Without ride-sharing")

# Break the script if the initial solution proved to be infeasible
if fx['feasibility_check'](sol, gs, fx, ride_sharing = Ride_sharing, full = True) > 0:
    raise Exception("Break through infeasibilities, see above")


print(f"The initial distance after the construction algorithm equals {round(sol['obj_val'])} km")
print(f"Number of time window violations: {sum([len(sol['tw_viol'][ref]) for ref in range(gs['nrefs'])])}")
print(f"Sum of gamma violations: {sum([sol['gamma_viol'][ref] for ref in range(gs['nrefs']) if sol['gamma_viol'][ref] > 0])}")
print(f"Sum of availability violations: {sum([len(sol['avail_viol'][ref]) for ref in range(gs['nrefs'])])}")
print(f"Sum of fallback violations: "
      f"{sum([sol['fb_viol'] - gs['max_fb'] if sol['fb_viol'] > gs['max_fb'] else 0])}")
print(f"Sum of weekend violations: " f"{sum([sol['weekend_viol'][ref] for ref in range(gs['nrefs'])])}")
print(f"Number of for hire refs: {len(sol['ref_assignments'][gs['nrefs'] - 1])}")
print(f"Total violation costs: {round(sum(sol['penalty_cost']))}")
print(f"Total driven kilometres: {round(sol['obj_val'] - sum(sol['penalty_cost']))} km")
rs_kms = sum([sol['rs_dist'][ref][day] - sol['assignments_base_dist'][ref][day] for ref in range(gs['nrefs'])
              for day in range(365) if len(sol['rs_given'][ref][day]) > 0])
saved_kms = sum([sol['assignments_base_dist'][ref][day] for ref in range(gs['nrefs']) for day in range(365)
                 if sol['rs_received'][ref][day] != -1])
print(f"Kilometres saved by ride-sharing: {round(saved_kms - rs_kms)} km")

'''
Some statistics
'''
t_now = 0
t_start = time.time()

sol_best = [(ref, game) for ref in range(gs['nrefs']) for game in sol['ref_assignments'][ref]]
obj_best = [sol['obj_val']]
obj_cur = [sol['obj_val']]
sol_diff = []
best_obj_val = sol['obj_val']



'''
Here you specify which operators to use
'''
destroy_operators = ['random_removal', 'greedy_distance_removal', 'highest_assignment_removal', 'random_violation_removal']
repair_operators = ['random_insertion', 'greedy_distance_insert', 'least_assignment_insertion']
if Ride_sharing:
    destroy_operators.extend(['highest_rs_removal', 'cluster_day_removal'])
    repair_operators.extend(['same_assignment_insertion'])

'''
Starting options:
- Run time
- Starting weights of the operators (w_destroy, w_repair)
- Scores per acceptance realization (scores)
- Updating multiplicator scores (theta)
- Removed games per iteration (n)
'''

t_max = 60 * 5 # Run for t_max seconds
w_destroy = [10] * len(destroy_operators)
w_repair = [10] * len(repair_operators)
scores = [20, 8, 3, 1]
theta = 0.9
n = 20

w_destroy_ls = []
w_repair_ls = []

it = 0
print(f"Expected end time of algorithm is {datetime.now() + timedelta(seconds=t_max)}")
while t_now < t_max:
    '''
    Simple ALNS algorithm which just runs for a set amount of time
    '''
    t_now = time.time() - t_start
    it += 1

    '''
    First we destroy the solution
    '''
    sol_prime = sol
    destroy_op = fx['operator_choice'](w_destroy, destroy_operators)
    tmp_destroy = fx[destroy_op](n, sol_prime, gs, fx)
    sol_prime = tmp_destroy[0]
    removed_games = tmp_destroy[1]
    removed_refs = tmp_destroy[2]

    '''
    Then we repair the solution again
    '''
    repair_op = fx['operator_choice'](w_repair, repair_operators)
    tmp_repair = fx[repair_op](removed_games, sol_prime, gs, fx)
    sol_prime = tmp_repair[0]
    inserted_refs = tmp_repair[1]
    inserted_games = tmp_repair[2]
    if fx['feasibility_check'](sol_prime, gs, fx, ride_sharing = Ride_sharing, full = False) > 0:
        raise Exception("Break through infeasibilities, see above")

    if it % 1000 == 0: # Once in the 1000 iterations do a full check
        if fx['feasibility_check'](sol_prime, gs, fx, ride_sharing=Ride_sharing, full=True) > 0:
            raise Exception("Break through infeasibilities, see above")

    '''
    Then we decide what to do with the new solution (Reject/Accept/Local best/Global best)
    '''

    # if it % 100 == 0:
    #     # Printing acceptance probability
    #     T_now = (n ** 0.5) * gs['max_dist'] / (1 + (t_now / t_max)) ** 2
    #     print(sol_prime['obj_val'] - obj_cur[len(obj_cur) - 1])
    #     print(math.exp(-(sol_prime['obj_val'] - obj_cur[len(obj_cur) - 1]) / T_now))

    if fx['simulated_annealing'](n, t_now, t_max, obj_cur[len(obj_cur) - 1], sol_prime, gs):
        decision = 2  # Solution Accepted
        if sol_prime['obj_val'] < sol['obj_val']:
            decision = 1  # Solution better than current
        sol = sol_prime #copy.deepcopy(sol_prime)
    else:
        # Not accepted ==> solution has to be put in original state again
        decision = 3  # Solution Rejected
        # First we destroy the insertions again:
        sol_prime = fx['destroy_sol']([(inserted_refs[i], inserted_games[i]) for i in range(len(inserted_refs))],
                                      sol_prime, gs, fx)
        # Then we repair it with the previous deletions:
        sol_prime = fx['fix_sol']([(removed_refs[i], removed_games[i]) for i in range(len(inserted_refs))], sol_prime, gs, fx)
        sol = sol_prime
        fx['feasibility_check'](sol, gs, fx, ride_sharing = Ride_sharing, full = False)

    if sol['obj_val'] < best_obj_val: # If this new objective is better than everything before
        best_obj_val = sol['obj_val']
        sol_best = [(ref, game) for ref in range(gs['nrefs']) for game in sol['ref_assignments'][ref]] # Make this the new best solution
        decision = 0 # New global best

    '''
    Now we update the weights
    '''
    w_destroy, w_repair = fx['weights_update'](decision, (destroy_op, repair_op), [destroy_operators, repair_operators],
                                               [w_destroy, w_repair], scores, theta)
    w_destroy_ls.append(w_destroy.copy())
    w_repair_ls.append(w_repair.copy())

    '''
    Saving statistics for plotting
    '''
    obj_best.append(best_obj_val)
    obj_cur.append(sol['obj_val'])


best_sol = empty_sol_maker(gs)

if not Ride_sharing and Improve_rs: # If improve using ride_sharing, the ride-sharing fix_sol version is taken
    if Feasible:
        # from Functions.Infeasible.Ride_sharing.Fix_sol_rs import fix_sol
        from Functions.Ride_sharing.Rs_possible_distance import rs_possible_distance
        # fx['fix_sol'] = fix_sol
        fx['rs_possible_distance'] = rs_possible_distance
    else:
        from Functions.Infeasible.Ride_sharing.Fix_sol_rs import fix_sol
        from Functions.Ride_sharing.Rs_possible_distance import rs_possible_distance
        fx['fix_sol'] = fix_sol
        fx['rs_possible_distance'] = rs_possible_distance

'''
Writing solution to file
'''
str_wrt = f"Solution_{inst}"
if Ride_sharing:
    str_wrt += "_rs"
elif Improve_rs:
    str_wrt += "_imp"
if Feasible:
    str_wrt += "_feasible"
else:
    str_wrt += "_infeasible"
str_wrt += "_" + str(t_max)

for tup in sol_best:
    best_sol = fx['fix_sol']((tup[0], tup[1]), best_sol, gs, fx)  # Update solution

if fx['feasibility_check'](best_sol, gs, fx, ride_sharing=Ride_sharing, full=True) > 0:
    raise Exception("Break through infeasibilities, see above")



print([w_destroy, w_repair])
print(f"Best found solution equals {round(best_sol['obj_val'])} km")
print(f"Number of iterations equals {it}")
print(f"Number of time window violations: {sum([len(best_sol['tw_viol'][ref]) for ref in range(gs['nrefs'])])}")
print(f"Sum of gamma violations: {sum([best_sol['gamma_viol'][ref] for ref in range(gs['nrefs']) if best_sol['gamma_viol'][ref] > 0])}")
print(f"Sum of availability violations: {sum([len(best_sol['avail_viol'][ref]) for ref in range(gs['nrefs'])])}")
print(f"Sum of fallback violations: "
      f"{sum([best_sol['fb_viol'] - gs['max_fb'] if best_sol['fb_viol'] > gs['max_fb'] else 0])}")
print(f"Sum of weekend violations: " f"{sum([best_sol['weekend_viol'][ref] for ref in range(gs['nrefs'])])}")
print(f"Number of for hire refs: {len(best_sol['ref_assignments'][gs['nrefs'] - 1])}")
print(f"Total violation costs: {round(sum(best_sol['penalty_cost']))}")
print(f"Total driven kilometres: {round(best_sol['obj_val'] - sum(best_sol['penalty_cost']))} km")
rs_kms = sum([best_sol['rs_dist'][ref][day] - best_sol['assignments_base_dist'][ref][day] for ref in range(gs['nrefs'])
              for day in range(365) if len(best_sol['rs_given'][ref][day]) > 0])
saved_kms = sum([best_sol['assignments_base_dist'][ref][day] for ref in range(gs['nrefs']) for day in range(365)
                 if best_sol['rs_received'][ref][day] != -1])
print(f"Kilometres saved by ride-sharing: {round(saved_kms - rs_kms)} km")

print('-*' * 50)
print(f"Current solution equals {round(sol['obj_val'])} km")
print(f"Number of time window violations: {sum([len(sol['tw_viol'][ref]) for ref in range(gs['nrefs'])])}")
print(f"Sum of gamma violations: {sum([sol['gamma_viol'][ref] for ref in range(gs['nrefs']) if sol['gamma_viol'][ref] > 0])}")
print(f"Sum of availability violations: {sum([len(sol['avail_viol'][ref]) for ref in range(gs['nrefs'])])}")
print(f"Sum of fallback violations: "
      f"{sum([sol['fb_viol'] - gs['max_fb'] if sol['fb_viol'] > gs['max_fb'] else 0])}")
print(f"Sum of weekend violations: " f"{sum([sol['weekend_viol'][ref] for ref in range(gs['nrefs'])])}")
print(f"Number of for hire refs: {len(sol['ref_assignments'][gs['nrefs'] - 1])}")
print(f"Total violation costs: {round(sum(sol['penalty_cost']))}")
print(f"Total driven kilometres: {round(sol['obj_val'] - sum(sol['penalty_cost']))} km")
rs_kms = sum([sol['rs_dist'][ref][day] - sol['assignments_base_dist'][ref][day] for ref in range(gs['nrefs'])
              for day in range(365) if len(sol['rs_given'][ref][day]) > 0])
saved_kms = sum([sol['assignments_base_dist'][ref][day] for ref in range(gs['nrefs']) for day in range(365)
                 if sol['rs_received'][ref][day] != -1])
print(f"Kilometres saved by ride-sharing: {round(saved_kms - rs_kms)} km")


plt.plot([i for i in range(0, len(obj_best))], obj_best, color='blue', label='Best objective')

# Plotting the second line (red color)
plt.plot([i for i in range(0, len(obj_cur))], obj_cur, color='orange', label='Current objective')

# Adding labels and title
plt.xlabel('Iteration')
plt.ylabel('Objective value')
plt.title('Progress of objective value over time')
plt.legend()
plt.savefig(f"Progress_obj_val_{inst}_{t_max}")
plt.show()


'''
Repair and destroy operator probability chosen over time
'''
for op in range(len(destroy_operators)):
    plt.plot([i for i in range(len(w_destroy_ls))], [w_destroy_ls[i][op] for i in range(len(w_destroy_ls))], label = destroy_operators[op])

plt.xlabel("Iteration")
plt.ylabel("Operator weight")
plt.title("Operators weights over time")
plt.legend()
plt.savefig(f"Operator_weights_destroy_{inst}_{t_max}")
plt.show()

for op in range(len(repair_operators)):
    plt.plot([i for i in range(len(w_repair_ls))], [w_repair_ls[i][op] for i in range(len(w_repair_ls))], label = repair_operators[op])

plt.xlabel("Iteration")
plt.ylabel("Operator weight")
plt.title("Operators weights over time")
plt.legend()
plt.savefig(f"Operator_weights_repair_{inst}_{t_max}")
plt.show()

# No ride-sharing, 5 mins
# Best found solution equals 175768 km
# Number of iterations equals 2833
# Kilometres saved by ride-sharing: 25104 km

# With ride-sharing, 5 mins:
# Best found solution equals 166843 km
# Number of iterations equals 1831
# Kilometres saved by ride-sharing: 37641 km

