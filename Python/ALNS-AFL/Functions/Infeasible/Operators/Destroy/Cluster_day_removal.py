'''
This function randomly selects a day (on which there are games) and aims to remove referees there which do not ride-share yet
This might open up the potential for new ride-sharings
'''

import random
def cluster_day_removal(n, sol, gs, fx):
    destroyed_games = []
    destroyed_refs = []
    poss_days = list(gs['game_df']['date'].unique())
    while len(destroyed_games) < n:
        day = random.choice(poss_days)
        poss_days.remove(day)
        sol, destroyed_games, destroyed_refs = one_day_removal(n - len(destroyed_games), day, sol, gs, fx, destroyed_games, destroyed_refs)



    return sol, destroyed_games, destroyed_refs

def one_day_removal(m, day, sol, gs, fx, destroyed_games, destroyed_refs):
    refs_with_ass = [ref for ref in range(gs['nrefs']) if sol['assignments_day'][ref][day] > 0]  # Refs on this day
    ref_no_rs = [ref for ref in refs_with_ass if sol['rs_dist'][ref][day] == 0]  # Refs with no rs
    ref_ass_no_rs = [(ref, game) for ref in ref_no_rs for game in sol['ref_day_assignments'][ref][day]]
    if len(ref_ass_no_rs) < m:  # Fill it up with a few more refs on this same day
        for _ in range(min(m - len(ref_ass_no_rs), len(refs_with_ass) - len(ref_no_rs))):
            # Try to fill it up till m, if this is not possible fill it up with the max amount of refs
            ref_app = random.choice([ref for ref in refs_with_ass if ref not in ref_no_rs]) # Possible refs to add
            ref_no_rs.append(ref_app)
            game_app = random.choice(sol['ref_day_assignments'][ref_app][day])
            ref_ass_no_rs.append((ref_app, game_app))  # Include in list to be removed now

    for ref_game in ref_ass_no_rs:
        destroyed_games.append(ref_game[1])
        destroyed_refs.append(ref_game[0])
        sol = fx['destroy_sol']((ref_game[0], ref_game[1]), sol, gs, fx)

    return sol, destroyed_games, destroyed_refs