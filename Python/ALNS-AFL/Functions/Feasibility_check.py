'''
This function checks if a given solution is feasible.

It does so by performing the following feasibility checks:
1. An official is only assigned if he is available that day
2. Time windows of games may not overlap
3. An official may have only one officiating role
4. Officials may only officiate games within their allowed leagues
- t1 match requires only t1 official
- t2 match requires only t2 official
- leagues not in "own team" require that official is not officiating a match of his/her own team
5. Official officiates at least gamma_0 games
6. License class requirements
- If t1/t2 or (Regionalliga and division senior):
    - E = 0
- If cup and # participating teams < 3:
    - E <= 1
- Else:
    - E <= 2
7. White hat requirements
- t1 match requires at least one t1+wh official
- t2 match requires at least one t2+wh official
- whp match requires at least one wh official
- match (not t1/t2/whp) requires at least one wh/whp official
- cup match with more than 3 teams requires at least two wh/whp officials
8. Fall-back assignments is less than nu
9. Ride-sharing capacity is met at all times (also considers mobility)
10. Ride-sharing only happens if referees are assigned to the same game
11. Ride-sharing only happens if additional distance for ride-sharing offerer is less than m%
12. Weekend restrictions are met (if availability day = '*', then no assignments to other days with '*' around it)
13. No negative weekend restrictions
14. Ride-sharing distances of routes equal distance of trav_dist
15. Base distance always equal distance of assigned games
16. Objective value is sum of travel distances and penalty costs

Options:
Full (T/F): if False, it does not calculate the expensive checking which check all refs and days
'''



def feasibility_check(sol, gs, fx, ride_sharing, full = False):
    n_infeasibilities = 0
    if full:
        range_check = [i for i in range(1, 17)]
    else:
        range_check = [i for i in range(1, 9)] + [12, 13, 16]

    if not ride_sharing:
        rs_checks = [9, 10, 11, 14, 15]
        range_check = [i for i in range_check if i not in rs_checks]

    for i in range_check:
        n_infeasibilities += fx[f'feasibility_{i}'](sol, gs, fx)

    return n_infeasibilities