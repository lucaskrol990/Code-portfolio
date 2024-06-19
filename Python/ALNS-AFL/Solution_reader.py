import pandas as pd
import os
import numpy as np
import scipy.stats as stats


def empty_sol_maker_Gabor(gs):
    import numpy as np

    ## First we initialize sol as empty lists etc.
    # Referee assignments
    ref_assignments = [[] for _ in range(gs['nrefs'])]  # Empty lists for every referee

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
    rs_occur = []  # No tuples to begin with

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
    gamma_viol.append(0)  # For hire referee has no assignment slack
    gamma_viol = np.array(gamma_viol)

    # Fall back violation
    fb_viol = 0

    # Weekend violation
    weekend_viol = [0 for _ in range(gs['nrefs'])]

    # penalty cost:
    penalty_cost = np.array([gamma_viol[ref] * gs['penalty_gamma'] for ref in range(gs['nrefs'])])

    # Violation pairs
    violation_pairs = []  # No violation pairs atm

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

def calculate_ci(data, confidence=0.95):
    data = np.array(data)
    n = len(data)
    mean = np.mean(data)
    sem = stats.sem(data)
    critical_value = stats.t.ppf((1 + confidence) / 2, df=n-1)
    moe = critical_value * sem
    return [round(mean - moe), round(mean + moe)]

from globals_maker import gs_maker
from Function_load import function_load
from Infeasible_solution import empty_sol_maker


year = 2022
gs = gs_maker(year, False)
fx = function_load(feasible=False, ride_sharing=True)


'''
Multiple
'''

nexps = 5
nits = 10

obj_val = [[] for _ in range(nexps)]
for exp in range(nexps):
    for it in range(nits):
        sol_load = pd.read_csv(f"Habrok_variants/Solutions/Hyperparameter_n_5_20/Solution_p{exp}_n20_{it}")
        sol_load = sol_load.loc[:, ['Referee', 'Game']]
        sol_best = []
        for row in sol_load.itertuples(index=False, name=None):
            sol_best.append(row)

        best_sol = empty_sol_maker(gs, fx, ride_sharing=True)
        for tup in sol_best:
            best_sol = fx['fix_sol']((tup[0], tup[1]), best_sol, gs, fx)  # Update solution
        # print((exp, it))
        # print(best_sol['obj_val'])
        obj_val[exp].append(round(best_sol['obj_val']))
    print(calculate_ci(obj_val[exp]))

'''
Multiple, no CI. Written to table
'''
# # filenames = ["Solution_2010_imp_infeasible_120", "Solution_2022_rs_infeasible_3600"]
# from Habrok_variants.globals_maker_sensitivity_mobility import gs_maker
#
# filepath = f"Habrok_variants/Solutions/Sensitivity_mob"
# filenames = os.listdir(filepath)[78:104]
# print(filenames)
# # rs = [False] * 1 + [True] * 1
# it = 0
#
# write_df = {'Year': [], 'Objective value': [], 'Driven kilometres': [], 'Violation costs': [], 'Saved by ride-sharing': [],
#             'Time window': [], 'Gamma': [], 'Availability': [], 'Fallback': [], 'Weekend': [], 'For hire refs': []}
# write_df_rs = {'Year': [], 'Objective value': [], 'Driven kilometres': [], 'Violation costs': [], 'Saved by ride-sharing': [],
#             'Time window': [], 'Gamma': [], 'Availability': [], 'Fallback': [], 'Weekend': [], 'For hire refs': []}
# for filename in filenames:
#     print('-*' * 50)
#     print(filename)
#     # year = int(filename.split("_")[1])
#     year = int(filename.split("_")[2])
#     gs = gs_maker(year, False, mobility = 0.75)
#     if "imp" in f"{filepath}/{filename}":
#         rs = False
#     else:
#         rs = True
#     fx = function_load(feasible=False, ride_sharing=True) # Do still want to improve the solution with ride-sharing
#     sol_load = pd.read_csv(f"{filepath}/{filename}")
#     sol_load = sol_load.loc[:, ['Referee', 'Game']]
#     sol_best = []
#     for row in sol_load.itertuples(index=False, name=None):
#         sol_best.append(row)
#
#     best_sol = empty_sol_maker(gs, fx, ride_sharing=rs)
#     for tup in sol_best:
#         best_sol = fx['fix_sol']((tup[0], tup[1]), best_sol, gs, fx)  # Update solution
#
#     print(f"Best found solution equals {round(best_sol['obj_val'])} km")
#     print(f"Number of time window violations: {sum([len(best_sol['tw_viol'][ref]) for ref in range(gs['nrefs'])])}")
#     print(f"Sum of gamma violations: {sum([best_sol['gamma_viol'][ref] for ref in range(gs['nrefs']) if best_sol['gamma_viol'][ref] > 0])}")
#     print(f"Sum of availability violations: {sum([len(best_sol['avail_viol'][ref]) for ref in range(gs['nrefs'])])}")
#     print(f"Sum of fallback violations: "
#           f"{sum([best_sol['fb_viol'] - gs['max_fb'] if best_sol['fb_viol'] > gs['max_fb'] else 0])}")
#     print(f"Sum of weekend violations: " f"{sum([best_sol['weekend_viol'][ref] for ref in range(gs['nrefs'])])}")
#     print(f"Number of for hire refs: {len(best_sol['ref_assignments'][gs['nrefs'] - 1])}")
#     print(f"Total violation costs: {round(sum(best_sol['penalty_cost']))}")
#     print(f"Total driven kilometres: {round(best_sol['obj_val'] - sum(best_sol['penalty_cost']))} km")
#     rs_kms = sum([best_sol['rs_dist'][ref][day] - best_sol['assignments_base_dist'][ref][day] for ref in range(gs['nrefs'])
#                   for day in range(365) if len(best_sol['rs_given'][ref][day]) > 0])
#     saved_kms = sum([best_sol['assignments_base_dist'][ref][day] for ref in range(gs['nrefs']) for day in range(365)
#                      if best_sol['rs_received'][ref][day] != -1])
#     print(f"Kilometres saved by ride-sharing: {round(saved_kms - rs_kms)} km")
#     it += 1
#     if rs:
#         write_df_rs['Year'].append(year)
#         write_df_rs['Objective value'].append(best_sol['obj_val'])
#         write_df_rs['Driven kilometres'].append(round(best_sol['obj_val'] - sum(best_sol['penalty_cost'])))
#         write_df_rs['Violation costs'].append(sum(best_sol['penalty_cost']))
#         write_df_rs['Saved by ride-sharing'].append(saved_kms - rs_kms)
#         write_df_rs['Time window'].append(sum([len(best_sol['tw_viol'][ref]) for ref in range(gs['nrefs'])]))
#         write_df_rs['Gamma'].append(
#             sum([best_sol['gamma_viol'][ref] for ref in range(gs['nrefs']) if best_sol['gamma_viol'][ref] > 0]))
#         write_df_rs['Availability'].append(sum([len(best_sol['avail_viol'][ref]) for ref in range(gs['nrefs'])]))
#         write_df_rs['Fallback'].append(
#             sum([best_sol['fb_viol'] - gs['max_fb'] if best_sol['fb_viol'] > gs['max_fb'] else 0]))
#         write_df_rs['Weekend'].append(sum([best_sol['weekend_viol'][ref] for ref in range(gs['nrefs'])]))
#         write_df_rs['For hire refs'].append(len(best_sol['ref_assignments'][gs['nrefs'] - 1]))
#     else:
#         write_df['Year'].append(year)
#         write_df['Objective value'].append(best_sol['obj_val'])
#         write_df['Driven kilometres'].append(round(best_sol['obj_val'] - sum(best_sol['penalty_cost'])))
#         write_df['Violation costs'].append(sum(best_sol['penalty_cost']))
#         write_df['Saved by ride-sharing'].append(saved_kms - rs_kms)
#         write_df['Time window'].append(sum([len(best_sol['tw_viol'][ref]) for ref in range(gs['nrefs'])]))
#         write_df['Gamma'].append(sum([best_sol['gamma_viol'][ref] for ref in range(gs['nrefs']) if best_sol['gamma_viol'][ref] > 0]))
#         write_df['Availability'].append(sum([len(best_sol['avail_viol'][ref]) for ref in range(gs['nrefs'])]))
#         write_df['Fallback'].append(sum([best_sol['fb_viol'] - gs['max_fb'] if best_sol['fb_viol'] > gs['max_fb'] else 0]))
#         write_df['Weekend'].append(sum([best_sol['weekend_viol'][ref] for ref in range(gs['nrefs'])]))
#         write_df['For hire refs'].append(len(best_sol['ref_assignments'][gs['nrefs'] - 1]))
#
# df_written = pd.DataFrame(write_df)
# df_written_rs = pd.DataFrame(write_df_rs)
# df_merged = pd.merge(df_written, df_written_rs, how = 'inner', on = 'Year')
# delta_dist = round(100 * (df_merged['Objective value_y'] - df_merged['Objective value_x']) / df_merged['Objective value_x'], 2)
# delta_dist = [str(val) + '\%' for val in delta_dist]
# df_merged.insert(1, '$\Delta$', delta_dist)
# print(df_merged.to_latex(float_format="%.0f", index = False))


'''
Multiple, no CI. Written to table. Feasible instances
'''
# # filenames = ["Solution_2010_imp_infeasible_120", "Solution_2022_rs_infeasible_3600"]
# filepath = f"Habrok_variants/Solutions/Feasibile_sens_m"
# filenames = os.listdir(filepath)
#
# # rs = [False] * 1 + [True] * 1
# it = 0
#
# write_df = {'Instance': [], 'Driven kilometres': [], 'Saved by ride-sharing': []}
# write_df_rs = {'Instance': [], 'Driven kilometres': [], 'Saved by ride-sharing': []}
# instance_df = {'Instance': [], '\mid O \mid': [], '\mid D \mid': [], 'Average availability': [], '\mid G_d \mid': []}
# for filename in filenames:
#     print('-*' * 50)
#     print(filename)
#     if not '4.0' in filename:
#         continue
#     instance = int(filename.split("_")[2])
#     from globals_maker_Gabor import gs_maker
#     gs = gs_maker(instance)
#     gs['m'] = 0.4
#     if "imp" in f"{filepath}/{filename}":
#         rs = False
#     else:
#         rs = True
#     fx = function_load(feasible=False, ride_sharing=True) # Do still want to improve the solution with ride-sharing
#     sol_load = pd.read_csv(f"{filepath}/{filename}")
#     sol_load = sol_load.loc[:, ['Referee', 'Game']]
#     sol_best = []
#     for row in sol_load.itertuples(index=False, name=None):
#         sol_best.append(row)
#
#     best_sol = empty_sol_maker_Gabor(gs)
#     for tup in sol_best:
#         best_sol = fx['fix_sol']((tup[0], tup[1]), best_sol, gs, fx)  # Update solution
#
#     print(f"Best found solution equals {round(best_sol['obj_val'])} km")
#     print(f"Total driven kilometres: {round(best_sol['obj_val'] - sum(best_sol['penalty_cost']))} km")
#     rs_kms = sum([best_sol['rs_dist'][ref][day] - best_sol['assignments_base_dist'][ref][day] for ref in range(gs['nrefs'])
#                   for day in range(365) if len(best_sol['rs_given'][ref][day]) > 0])
#     saved_kms = sum([best_sol['assignments_base_dist'][ref][day] for ref in range(gs['nrefs']) for day in range(365)
#                      if best_sol['rs_received'][ref][day] != -1])
#     print(f"Kilometres saved by ride-sharing: {round(saved_kms - rs_kms)} km")
#     it += 1
#     if rs:
#         write_df_rs['Instance'].append(instance)
#         write_df_rs['Driven kilometres'].append(round(best_sol['obj_val'] - sum(best_sol['penalty_cost'])))
#         write_df_rs['Saved by ride-sharing'].append(saved_kms - rs_kms)
#
#         instance_df['Instance'].append(instance)
#         instance_df['\mid O \mid'].append(gs['referee_df'].shape[0] - 1)
#         instance_df['\mid D \mid'].append(len(gs['game_df']['date'].unique()))
#         avg_avail = sum([sum([gs['availability_matrix'][ref][game] for game in range(gs['ngames'])])
#                          / gs['ngames'] for ref in range(gs['nrefs'])]) / gs['nrefs']
#         instance_df['Average availability'].append(avg_avail)
#         avg_games_day = gs['game_df'].shape[0] / len(gs['game_df']['date'].unique())
#         instance_df['\mid G_d \mid'].append(avg_games_day)
#     else:
#         write_df['Instance'].append(instance)
#         write_df['Driven kilometres'].append(round(best_sol['obj_val'] - sum(best_sol['penalty_cost'])))
#         write_df['Saved by ride-sharing'].append(saved_kms - rs_kms)
#
# df_written = pd.DataFrame(write_df)
# df_written_rs = pd.DataFrame(write_df_rs)
# df_instance = pd.DataFrame(instance_df)
# df_merged = pd.merge(df_written, df_written_rs, how = 'inner', on = 'Instance')
# print(df_merged)
# df_merged_2 = pd.merge(df_instance, df_merged, how = 'inner', on = 'Instance')
# df_merged_2.sort_values(by = 'Instance', inplace=True)
# delta_dist = round(100 * (df_merged_2['Driven kilometres_y'] - df_merged_2['Driven kilometres_x']) / df_merged_2['Driven kilometres_x'], 2)
# delta_dist = [str(val) + '\%' for val in delta_dist]
# df_merged_2.insert(1, '$\Delta$', delta_dist)
# def custom_float_format(x):
#     if isinstance(x, float) and x in df_merged_2['Average availability'].values:
#         return f"{x:.2f}"
#     if isinstance(x, float) and x in df_merged_2['\mid G_d \mid'].values:
#         return f"{x:.2f}"
#     return f"{x:.0f}"
# print(df_merged_2.to_latex(float_format=custom_float_format, index = False))

'''
Singular, translated to ids
'''
# sol_load = pd.read_csv(f"Habrok_variants/Solutions/Hyperparameter_n/Solution_n0_4")
# sol_load = sol_load.loc[:, ['Referee', 'Game']]
# sol_best = []
# for row in sol_load.itertuples(index=False, name=None):
#     sol_best.append(row)
# best_sol = empty_sol_maker(gs, fx, ride_sharing=True)
# for tup in sol_best:
#     best_sol = fx['fix_sol']((tup[0], tup[1]), best_sol, gs, fx)  # Update solution
# print(len(sol_best))
# print(round(best_sol['obj_val']))
# print(f"Total driven kilometres: {round(best_sol['obj_val'] - sum(best_sol['penalty_cost']))} km")
# ref_ids = gs['referee_df'].loc[sol_load['Referee'], 'id'].tolist()
# game_ids = gs['game_df'].loc[sol_load['Game'], 'game_id'].tolist()
#
# x = pd.DataFrame({'Ref_id': ref_ids,
#                   'Game_id': game_ids})
# x.to_csv("Solutions/2022_id_assignments.csv")


'''
Check for missing filenames
'''

# filenames = os.listdir(f"Habrok_variants/Solutions/Sensitivity_mob")
# print(len(filenames))
# experiments = []
# for year in range(2010, 2023):
#     for rs_bool in [True, False]:
#         # for m in [0.1, 0.2, 0.3, 0.4]:
#         #     experiments.append({'Year': year, 'Ride_sharing': rs_bool, 'm': m})
#         for mobility in [0.25, 0.5, 0.75, 1]:
#             experiments.append({'Year': year, 'Ride_sharing': rs_bool, 'mobility': mobility})
# str_wrt_ls = []
# for exp_nr in range(len(experiments)):
#     Feasible = False
#     Ride_sharing = experiments[exp_nr]['Ride_sharing']
#     Improve_rs = True
#     year = experiments[exp_nr]['Year']
#     str_wrt = f"Solution_mob{int(experiments[exp_nr]['mobility']*100)}_{year}"
#     if Ride_sharing:
#         str_wrt += "_rs"
#     elif Improve_rs:
#         str_wrt += "_imp"
#     str_wrt += "_infeasible"
#     str_wrt_ls.append(str_wrt)
#
# print(str_wrt_ls)
# print(filenames)
# for exp_nr in range(len(experiments)):
#     file = str_wrt_ls[exp_nr]
#     if file not in filenames:
#         print(exp_nr)
#         print(file)