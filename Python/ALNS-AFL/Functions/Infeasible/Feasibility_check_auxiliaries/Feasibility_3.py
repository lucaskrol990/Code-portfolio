'''
Checks if the number of referees assigned per match equal the number of refs required
'''
def feasibility_3(sol, gs, fx):
    n_infeasibilities = 0
    for game in range(gs['ngames']):
        if len(sol['game_assignments'][game]) < gs['game_df'].loc[game, 'Number of referees']:
            n_infeasibilities += 1
            print(f"Number of assigned referees to game {game} was {len(sol['game_assignments'][game])} "
                  f"instead of the required {gs['game_df'].loc[game, 'Number of referees']}")
            print("These were the assignments:")
            print(sol['game_assignments'][game])
    return n_infeasibilities