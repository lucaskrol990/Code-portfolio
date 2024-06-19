'''
This scripts loads in all functions which are used in the algorithm at some point and stores it in fx
Options:
Feasible (T/F): if Feasible, the feasible version of functions is taken, otherwise the infeasible versions are taken
Ride sharing (T/F): if True, fix/destroy sol are based on ride sharing and operators related to ride sharing are activated
Operator choosing (String): which operator choosing algorithm to use
'''

def function_load(feasible, ride_sharing = False, operator_choosing = 'Roulette wheel'):
      from Functions.Distance_calculation import distance_calculation, time_calculation
      from Functions.Feasibility_check import feasibility_check
      from Functions.Referee_id_to_idx import referee_id_to_idx

      from Functions.Best_index_list import best_index_list
      from Functions.Acceptance_criterion.Simulated_annealing import simulated_annealing
      if operator_choosing == 'Roulette wheel':
            from Functions.Operator_choosing.Roulette_wheel import operator_choice, weights_update

      if feasible:
            from Functions.Feasible.Feasibility_check_auxiliaries.Feasibility_1 import feasibility_1
            from Functions.Feasible.Feasibility_check_auxiliaries.Feasibility_2 import feasibility_2
            from Functions.Feasible.Feasibility_check_auxiliaries.Feasibility_3 import feasibility_3
            from Functions.Feasible.Feasibility_check_auxiliaries.Feasibility_4 import feasibility_4
            from Functions.Feasible.Feasibility_check_auxiliaries.Feasibility_5 import feasibility_5
            from Functions.Feasible.Feasibility_check_auxiliaries.Feasibility_6 import feasibility_6
            from Functions.Feasible.Feasibility_check_auxiliaries.Feasibility_7 import feasibility_7
            from Functions.Feasible.Feasibility_check_auxiliaries.Feasibility_8 import feasibility_8
            from Functions.Feasible.Feasibility_check_auxiliaries.Feasibility_9 import feasibility_9
            from Functions.Feasible.Feasibility_check_auxiliaries.Feasibility_10 import feasibility_10
            from Functions.Feasible.Feasibility_check_auxiliaries.Feasibility_11 import feasibility_11
            from Functions.Infeasible.Feasibility_check_auxiliaries.Feasibility_12 import feasibility_12
            from Functions.Infeasible.Feasibility_check_auxiliaries.Feasibility_13 import feasibility_13
            from Functions.Infeasible.Feasibility_check_auxiliaries.Feasibility_14 import feasibility_14
            from Functions.Infeasible.Feasibility_check_auxiliaries.Feasibility_15 import feasibility_15
            from Functions.Infeasible.Feasibility_check_auxiliaries.Feasibility_16 import feasibility_16
            from Functions.Feasible.Feasibility_check_auxiliaries.Overlapping_game import overlapping_game

            from Functions.Feasible.Operators.Destroy.Random_removal import random_removal
            from Functions.Infeasible.Operators.Destroy.Greedy_distance_removal import greedy_distance_removal
            from Functions.Infeasible.Operators.Destroy.Highest_assignment_removal import highest_assignment_removal
            from Functions.Infeasible.Operators.Destroy.Random_violation_removal import random_violation_removal
            from Functions.Infeasible.Operators.Destroy.Highest_rs_removal import highest_rs_removal
            from Functions.Infeasible.Operators.Destroy.Cluster_day_removal import cluster_day_removal
            from Functions.Feasible.Operators.Repair.Random_insertion import random_insertion
            from Functions.Infeasible.Operators.Repair.Greedy_distance_insert import greedy_distance_insert
            from Functions.Infeasible.Operators.Repair.Least_assignment_insertion import least_assignment_insertion
            from Functions.Infeasible.Operators.Repair.Same_assignment_insertion import same_assignment_insertion

            from Functions.Feasible.Feasible_refs import feasible_refs

            if ride_sharing:
                  from Functions.Feasible.Fix_sol import fix_sol
                  from Functions.Feasible.Destroy_sol import destroy_sol
                  from Functions.Ride_sharing.Rs_possible_distance import rs_possible_distance
            else:
                  from Functions.Feasible.Fix_sol import fix_sol
                  from Functions.Feasible.Destroy_sol import destroy_sol

      else:
            from Functions.Infeasible.Feasibility_check_auxiliaries.Feasibility_1 import feasibility_1
            from Functions.Infeasible.Feasibility_check_auxiliaries.Feasibility_2 import feasibility_2
            from Functions.Infeasible.Feasibility_check_auxiliaries.Feasibility_3 import feasibility_3
            from Functions.Infeasible.Feasibility_check_auxiliaries.Feasibility_4 import feasibility_4
            from Functions.Infeasible.Feasibility_check_auxiliaries.Feasibility_5 import feasibility_5
            from Functions.Infeasible.Feasibility_check_auxiliaries.Feasibility_6 import feasibility_6
            from Functions.Infeasible.Feasibility_check_auxiliaries.Feasibility_7 import feasibility_7
            from Functions.Infeasible.Feasibility_check_auxiliaries.Feasibility_8 import feasibility_8
            from Functions.Infeasible.Feasibility_check_auxiliaries.Feasibility_9 import feasibility_9
            from Functions.Infeasible.Feasibility_check_auxiliaries.Feasibility_10 import feasibility_10
            from Functions.Infeasible.Feasibility_check_auxiliaries.Feasibility_11 import feasibility_11
            from Functions.Infeasible.Feasibility_check_auxiliaries.Feasibility_12 import feasibility_12
            from Functions.Infeasible.Feasibility_check_auxiliaries.Feasibility_13 import feasibility_13
            from Functions.Infeasible.Feasibility_check_auxiliaries.Feasibility_14 import feasibility_14
            from Functions.Infeasible.Feasibility_check_auxiliaries.Feasibility_15 import feasibility_15
            from Functions.Infeasible.Feasibility_check_auxiliaries.Feasibility_16 import feasibility_16
            from Functions.Infeasible.Feasibility_check_auxiliaries.Overlapping_game import overlapping_game
            from Functions.Infeasible.Feasibility_check_auxiliaries.Weekend_overlap import weekend_overlap

            from Functions.Infeasible.Operators.Destroy.Random_removal import random_removal
            from Functions.Infeasible.Operators.Destroy.Greedy_distance_removal import greedy_distance_removal
            from Functions.Infeasible.Operators.Destroy.Highest_assignment_removal import highest_assignment_removal
            from Functions.Infeasible.Operators.Destroy.Random_violation_removal import random_violation_removal
            from Functions.Infeasible.Operators.Destroy.Highest_rs_removal import highest_rs_removal
            from Functions.Infeasible.Operators.Destroy.Cluster_day_removal import cluster_day_removal

            from Functions.Infeasible.Operators.Repair.Random_insertion import random_insertion
            from Functions.Infeasible.Operators.Repair.Greedy_distance_insert import greedy_distance_insert
            from Functions.Infeasible.Operators.Repair.Least_assignment_insertion import least_assignment_insertion
            from Functions.Infeasible.Operators.Repair.Same_assignment_insertion import same_assignment_insertion


            from Functions.Infeasible.Feasible_refs import feasible_refs

            if ride_sharing:
                  from Functions.Infeasible.Ride_sharing.Fix_sol_rs import fix_sol
                  from Functions.Infeasible.Ride_sharing.Destroy_sol_rs import destroy_sol
                  from Functions.Ride_sharing.Rs_possible_distance import rs_possible_distance
            else:
                  from Functions.Infeasible.Fix_sol import fix_sol
                  from Functions.Infeasible.Destroy_sol import destroy_sol


      fx = {'distance_calculation': distance_calculation,
            'time_calculation': time_calculation,
            'feasibility_check': feasibility_check,
            'referee_id_to_idx': referee_id_to_idx,
            'feasibility_1': feasibility_1,
            'feasibility_2': feasibility_2,
            'feasibility_3': feasibility_3,
            'feasibility_4': feasibility_4,
            'feasibility_5': feasibility_5,
            'feasibility_6': feasibility_6,
            'feasibility_7': feasibility_7,
            'feasibility_8': feasibility_8,
            'feasibility_9': feasibility_9,
            'feasibility_10': feasibility_10,
            'feasibility_11': feasibility_11,
            'feasibility_12': feasibility_12,
            'feasibility_13': feasibility_13,
            'feasibility_14': feasibility_14,
            'feasibility_15': feasibility_15,
            'feasibility_16': feasibility_16,
            'overlapping_game': overlapping_game,
            'weekend_overlap': weekend_overlap,
            'feasible_refs': feasible_refs,
            'fix_sol': fix_sol,
            'best_index_list': best_index_list,
            'destroy_sol': destroy_sol,
            'random_removal': random_removal,
            'greedy_distance_removal': greedy_distance_removal,
            'highest_assignment_removal': highest_assignment_removal,
            'random_violation_removal': random_violation_removal,
            'highest_rs_removal': highest_rs_removal,
            'cluster_day_removal': cluster_day_removal,
            'random_insertion': random_insertion,
            'greedy_distance_insert': greedy_distance_insert,
            'least_assignment_insertion': least_assignment_insertion,
            'same_assignment_insertion': same_assignment_insertion,
            'simulated_annealing': simulated_annealing,
            'operator_choice': operator_choice,
            'weights_update': weights_update
            }

      if ride_sharing:
            fx['rs_possible_distance'] = rs_possible_distance

      return fx