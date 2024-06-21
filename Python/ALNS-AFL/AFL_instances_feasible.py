import numpy as np
import pandas as pd
# Setup
np.random.seed(2)

# Initialize
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', '{:.3f}'.format)
options = {'echo': True, 'eval': True}

# Load libraries
import pandas as pd
import numpy as np

num_offs_test = [50, 100, 200]
num_days_test = [10, 20, 50, 100]
# Avails_test stores start_i probs and end_i probs in one list
avails_test = [[[0.5, 0.1, 0.1, 0.3], [0.1, 0.1, 0.8]],
               [[0.3, 0.05, 0.05, 0.6], [0.2, 0.2, 0.6]]]
games_day_range = [[4, 8], [8, 16], [2, 25]]

instances = [[]]
i = 0
for off in num_offs_test:
    for days in num_days_test:
        for avails in avails_test:
            for games_day in games_day_range:
                avg_avail = avails[0][0] + 0.5 * (avails[0][1] + avails[0][2]) - 0.5 * avails[0][0] * (
                            avails[1][0] + avails[1][1])
                nlocs = days * np.mean(games_day) + off
                # Check if the number of officials available is likely to be higher than the officials required (use 6 instead of 4 refs         # per game in this check) and that the number of locations remains reasonable (for computational reasons)
                if (off * avg_avail > 6 * games_day[1] and
                        nlocs < 500):
                    i += 1
                    instances.append([off, days, avails, games_day])


for inst in range(1, 10):
    # Parameters
    setup_time = 0.5  # Time an official has to arrive before a game
    wrap_time = 0.5  # Time an official has to stay after a game
    game_time = 1.5  # Time of a game

    trav_speed = 50  # Travel speed in km/h
    max_fback = 20  # Parameter to adjust
    rid_sh_cap = 4  # Ridesharing capacity for all officials with mobility
    max_detour = 0.3  # Maximum detour offering ridesharing to all other officials, compared to direct route


    # Generic functions
    ###Sample function
    def sampleFrom(n, y):
        if len(y) == 1 and n != 0:
            sf = y
        else:
            sf = np.random.choice(y, size=n)
        return sf


    ###Euclidean Distance Creators
    def EDM_creator1a(dist_matr, loca):
        x_cord = loca['geoLat']
        y_cord = loca['geoLng']
        EDM = []
        for i in range(len(dist_matr)):
            x_cord1 = dist_matr['geoLat'][i]
            y_cord1 = dist_matr['geoLng'][i]
            EDM.append(np.sqrt((x_cord - x_cord1) ** 2 + (y_cord - y_cord1) ** 2))
        return EDM


    def EDM_creator1(dist_matr, loca):
        R = 6371
        phi1 = loca['geoLat'] * (np.pi / 180)
        EDM = []
        for i in range(len(dist_matr)):
            phi2 = dist_matr['geoLat'][i] * (np.pi / 180)
            delta_phi = (dist_matr['geoLat'][i] - loca['geoLat']) * (np.pi / 180)
            delta_lambda = (dist_matr['geoLng'][i] - loca['geoLng']) * (np.pi / 180)

            a = np.sin(delta_phi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2) ** 2
            c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
            d = R * c

            EDM.append(d)
        return EDM


    def EDM_creator2(dist_matr):
        R = 6371
        phi = dist_matr['geoLat'] * (np.pi / 180)
        lambda_ = dist_matr['geoLng'] * (np.pi / 180)
        EDM = []
        for i in range(len(dist_matr)):
            delta_phi = phi[i] - phi
            delta_lambda = lambda_[i] - lambda_

            a = np.sin(delta_phi / 2) ** 2 + np.cos(phi[i]) * np.cos(phi) * np.sin(delta_lambda / 2) ** 2
            c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
            d = R * c
            EDM.append(d)
        return EDM

    def EDM_creator3(loca1, loca2):
        R = 6371  # Earth's radius in kilometers
        phi1 = loca1['geoLat'] * (np.pi / 180)  # Convert degrees to radians
        phi2 = loca2['geoLat'] * (np.pi / 180)
        delta_phi = (loca2['geoLat'] - loca1['geoLat']) * (np.pi / 180)
        delta_lambda = (loca2['geoLng'] - loca1['geoLng']) * (np.pi / 180)

        # Haversine formula
        a = np.sin(delta_phi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2) ** 2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

        d = R * c  # Distance in kilometers
        return d


    # Games
    num_days = instances[inst][1]
    num_games = np.random.choice(range(instances[inst][3][0], instances[inst][3][1] + 1), num_days, replace=True)
    num_leags = 5
    num_cl_le = 20
    num_clubs = num_leags * num_cl_le
    num_venue = max(num_leags * 2, num_cl_le)

    team_inf_i = pd.DataFrame({
        'team_id': np.arange(1, num_clubs + 1),
        'league_id': np.repeat(np.arange(1, num_leags + 1), num_cl_le)
    })


    def sample_venues(n, num_venues):
        return np.random.choice(num_venues, n, replace=False)


    team_inf_i['venue_id'] = team_inf_i.groupby('league_id')['league_id'].transform(
        lambda x: sample_venues(len(x), num_venue))


    def generate_geo(min, max, size):
        return np.random.beta(2, 2, size) * (max - min) + min


    unique_venues = team_inf_i['venue_id'].unique()
    venue_coords = pd.DataFrame({
        'venue_id': unique_venues,
        'geoLat': generate_geo(47.5, 52.5, len(unique_venues)),
        'geoLng': generate_geo(6, 12, len(unique_venues))
    })

    team_inf_i = pd.merge(team_inf_i, venue_coords, on='venue_id')

    league_inf_i = pd.DataFrame({'league_id': np.arange(1, num_leags + 1)})
    league_inf_i['num_offs'] = 4
    league_inf_i['toplev1'] = np.where(league_inf_i['league_id'] == 1, 1, 0)
    league_inf_i['toplev2'] = np.where(league_inf_i['league_id'] == 2, 1, 0)
    league_inf_i['cupmode'] = 0
    league_inf_i['whprosp'] = np.where(league_inf_i['league_id'].isin(range(num_leags - 1, num_leags + 1)), 1, 0)
    league_inf_i['offownc'] = np.where(league_inf_i['league_id'] == num_leags, 1, 0)
    league_inf_i['lirest'] = np.where(league_inf_i['league_id'].isin(range(num_leags - 1, num_leags + 1)), 2,
                                      np.where(league_inf_i['league_id'] == num_leags - 2, 1, 0))
    league_inf_i['nwh'] = 1

    game_list = []
    game_id_counter = 1

    for day in range(1, num_days + 1):
        games_today = num_games[day - 1]
        available_teams = team_inf_i['team_id'].tolist()
        team1_ids = np.zeros(games_today, dtype=int)
        team2_ids = np.zeros(games_today, dtype=int)
        used_teams = []

        for game in range(games_today):
            valid_team1s = [t for t in available_teams if t not in used_teams]
            team1_ids[game] = np.random.choice(valid_team1s, 1)[0]
            used_teams.append(team1_ids[game])
            league_teams = team_inf_i['team_id'][
                team_inf_i['league_id'] == int(team_inf_i['league_id'][team_inf_i['team_id'] == team1_ids[game]].iloc[0])].tolist()
            valid_team2s = [t for t in league_teams if t not in used_teams and t != team1_ids[game]]
            team2_ids[game] = np.random.choice(valid_team2s, 1)[0]
            used_teams.append(team2_ids[game])

        venues = team_inf_i['venue_id'][team_inf_i['team_id'].isin(team1_ids)].tolist()
        leagues = team_inf_i['league_id'][team_inf_i['team_id'].isin(team1_ids)].tolist()
        times = np.random.choice([9, 11, 13, 15, 17], games_today, replace=True, p=[0.2, 0.2, 0.2, 0.2, 0.2])

        games_df = pd.DataFrame({
            'day': [day] * games_today,
            'team1': team1_ids,
            'team2': team2_ids,
            'venue': venues,
            'time': times,
            'league': leagues,
            'geoLat': team_inf_i['geoLat'][team_inf_i['team_id'].isin(team1_ids)].tolist(),
            'geoLng': team_inf_i['geoLng'][team_inf_i['team_id'].isin(team1_ids)].tolist(),
            'club1': team1_ids,
            'club2': [-1] * games_today,
            'club3': team2_ids,
            'club4': [-1] * games_today
        })

        games_df = pd.merge(games_df, league_inf_i, left_on='league', right_on='league_id')
        game_list.append(games_df)
        game_id_counter += games_today

    # game_info_i
    game_info_i = pd.concat(game_list, axis=0).reset_index(drop=True)
    game_info_i.to_csv(f"games_Gabor_{inst + 1}.csv", index=False)

    # Officials
    num_officials = instances[inst][0]
    referee_ids = np.arange(1, num_officials + 1)

    associations = [1] * num_officials
    licenses = np.random.choice(['A', 'B', 'C', 'D', 'E'], size=num_officials, replace=True,
                                p=[0.2, 0.3, 0.25, 0.15, 0.1])
    reqgames = [0] * num_officials
    maxgames = [100] * num_officials
    clubs = np.random.randint(1, num_clubs + 1, size=num_officials)

    official_inf_i = pd.DataFrame({
        'id': referee_ids,
        'association': associations,
        'license': licenses,
        'reqgames': reqgames,
        'maxgames': maxgames,
        'club': clubs
    })

    official_inf_i['HSR'] = np.where(official_inf_i['license'] == 'A', 1,
                                     np.where(official_inf_i['license'] == 'B',
                                              np.random.binomial(1, 0.5, len(official_inf_i)), 0))

    official_inf_i['HSRP'] = np.where(official_inf_i['HSR'] == 1, 0,
                                      np.where(official_inf_i['license'] == 'B',
                                               np.random.binomial(1, 0.5, len(official_inf_i)),
                                               np.where(official_inf_i['license'] == 'C',
                                                        np.random.binomial(1, 0.25, len(official_inf_i)), 0)))

    official_inf_i['GFL'] = np.where(official_inf_i['license'].isin(['A', 'B']), 1, 0)
    official_inf_i['GFL2'] = np.where(official_inf_i['license'].isin(['A', 'B', 'C']), 1, 0)

    official_inf_i['geoLat'] = np.random.normal(50, 50 / 9, len(official_inf_i))
    official_inf_i['geoLng'] = np.random.normal(9, 9 / 50, len(official_inf_i))

    official_inf_i['licind'] = np.where(official_inf_i['license'] == 'E', 1, 0)

    official_inf_i['mobility'] = np.random.choice(['true', 'false'], size=len(official_inf_i), replace=True,
                                                  p=[0.95, 0.05])
    print(official_inf_i)
    official_inf_i.to_csv(f"referees_Gabor_{inst + 1}.csv", index=False)

    # Availability
    values = [0, 13, 16, 24]
    probabilities = instances[inst][2][0]

    avail_start_i = pd.DataFrame(np.random.choice(values, size=(num_officials, num_days), p=probabilities),
                                 columns=range(1, num_days + 1))
    avail_start_i.insert(0, 'referee', referee_ids)
    print(avail_start_i)

    avail_end_i = avail_start_i.copy()
    for i in range(len(avail_end_i)):
        for j in range(1, len(avail_end_i.columns)):
            if avail_start_i.iloc[i, j] == 0:
                avail_end_i.iloc[i, j] = np.random.choice([13, 16, 24], p=instances[inst][2][1])
            elif avail_start_i.iloc[i, j] in [13, 16]:
                avail_end_i.iloc[i, j] = 24
            elif avail_start_i.iloc[i, j] == 24:
                avail_end_i.iloc[i, j] = 0

    ref_avail_vec = []
    for ref in range(num_officials):
        ref_avail = ''
        for day in range(1, num_days + 1):
            if avail_start_i.iloc[ref, day] == 0 and avail_end_i.iloc[ref, day] == 24:
                ref_avail += 'J'
            elif avail_start_i.iloc[ref, day] == 0 and avail_end_i.iloc[ref, day] == 13:
                ref_avail += 'J'
                # ref_avail.append('M')
            elif avail_start_i.iloc[ref, day] == 13 and avail_end_i.iloc[ref, day] == 16:
                ref_avail += 'A'
                # ref_avail.append('A')
            elif avail_start_i.iloc[ref, day] == 16 and avail_end_i.iloc[ref, day] == 24:
                ref_avail += 'B'
                # ref_avail.append('B')
            elif avail_start_i.iloc[ref, day] == 0 and avail_end_i.iloc[ref, day] == 16:
                ref_avail += 'D'
                # ref_avail.append('D')
            elif avail_start_i.iloc[ref, day] == 13 and avail_end_i.iloc[ref, day] == 24:
                ref_avail += 'H'
                # ref_avail.append('H')
            else:
                ref_avail += 'N'
                # ref_avail.append('N')
        ref_avail_vec.append(ref_avail)
    avail_df = pd.DataFrame({'referee': list(range(1, num_officials + 1)),
                             'avail': ref_avail_vec})
    avail_df.to_csv(f"avails_Gabor_{inst + 1}.csv", index=False)
