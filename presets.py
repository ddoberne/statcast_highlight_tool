import get_vid
import pyb_tools

def make_highlight_reel(start_date, end_date, n_highlights, format, daily = False, teams = [], players = [],
                        ascending = False, max_duration = 20, countdown = True, truncate_beginning = True):
    """Creates a highlight reel from start_date to end_date of n_highlights clips based on the preset format.
     Set daily to true to pick n_highlights per day. Teams and players can be filtered for. Ascending = True will provide the lowest values instead of the highest."""
    df = make_leaderboard(start_date, end_date, n_highlights, format, daily, teams, players, ascending)
    df['flavor'] = df[preset_dict[format]['flavor_columns']].apply(preset_dict[format]['flavor_func'], axis = 1)
    args = pyb_tools.get_search_args_list(df)
    captions = pyb_tools.generate_captions(args, list(df['flavor']))
    for caption in captions:
        print(caption)
    compilation = get_vid.create_compilation_from_args(args, captions = captions, teams = teams, players = players, max_duration = max_duration, countdown = countdown, truncate_beginning = truncate_beginning)
    return compilation

def make_leaderboard(start_date, end_date, n_highlights, format, daily = False, teams = [], players = [],
                     ascending = False):
    """Creates a dataframe leaderboard from start_date to end_date of n_highlights entries based on the preset format.
     Set daily to true to pick n_highlights per day. Teams and players can be filtered for. Ascending = True will provide the lowest values instead of the highest."""
    pyb_tools.pybaseball.cache.enable()
    df = pyb_tools.get_statcast_data(start_date, end_date)
    df = pyb_tools.determine_pitching_batting_team(df)
    # Next line calls a function from a dict
    df = preset_dict[format]['tool'](df, teams, players)
    df = df.sort_values(by = preset_dict[format]['flavor_columns'], ascending = ascending)
    if len(teams) + len(players) > 0:
        if len(teams) > 0:
            home = 'home_team'
            away = 'away_team'
            group = teams
        else:
            home = 'pitcher'
            away = 'batter'
            group = players
        df['filter'] = df[[home, away]].apply(pyb_tools.cols_in_group, axis = 1, group = group)
        df = df.loc[df['filter']]
    


    if daily:
        df_replacement = pyb_tools.pd.DataFrame(columns = df.columns)
        for date in df['game_date'].unique():
            df_temp = df.loc[df['game_date'] == date].head(n_highlights)
            df_replacement = pyb_tools.pd.concat([df_replacement, df_temp])
        df = df_replacement.sort_values(by = 'game_date', ascending = True)
    else:
        df = df.head(n_highlights)
    return df

preset_dict = {}
preset_dict['ump_show'] = {'tool': pyb_tools.ump_show,
                           'flavor_columns': ['miss_by'],
                           'flavor_func': pyb_tools.ump_show_flavor,
                           'description': 'Umps calling strike 3 on pitches outside the strike zone.'}

preset_dict['called_corners'] = {'tool': pyb_tools.called_corners,
                                 'flavor_columns': ['off_center'],
                                 'flavor_func': lambda x: '',
                                 'description': 'Umps calling strikes on pitches that barely catch the strike zone.'}

preset_dict['clutch'] = {'tool': pyb_tools.clutch,
                         'flavor_columns': ['delta_win_exp'],
                         'flavor_func': pyb_tools.clutch_flavor,
                         'description': 'Plate appearances with the highest change in WPA.'}

preset_dict['blind_umps'] = {'tool': pyb_tools.worst_called_balls,
                             'flavor_columns': ['off_center'],
                             'flavor_func': lambda x: '',
                             'description': 'Umps calling pitches close to the center of the strike zone balls'}

preset_dict['takes_of_steel'] = {'tool': pyb_tools.takes_of_steel,
                                 'flavor_columns': ['off_center'],
                                 'flavor_func': lambda x: '',
                                 'description': 'Batters taking close pitches with 2 strikes.'}

preset_dict['scorchers'] = {'tool': pyb_tools.scorchers,
                            'flavor_columns': ['launch_speed', 'launch_angle'],
                            'flavor_func': pyb_tools.batted_ball_flavor,
                            'description': 'High exit velo contact with positive launch angle.'}

preset_dict['undergrounders'] = {'tool': pyb_tools.undergrounders,
                            'flavor_columns': ['launch_speed', 'launch_angle'],
                            'flavor_func': pyb_tools.batted_ball_flavor,
                            'description': 'High exit velo contact with launch angles below -10.'}

preset_dict['walks'] = {'tool': pyb_tools.walks,
                        'flavor_columns': ['miss_by'],
                        'flavor_func': pyb_tools.ump_show_flavor,
                        'description': 'Walks sorted by how much the pitch misses by.'}

preset_dict['full_count_walks'] = {'tool': pyb_tools.full_count_walks,
                        'flavor_columns': ['miss_by'],
                        'flavor_func': pyb_tools.ump_show_flavor,
                        'description': 'Walks on full counts sorted by how much the pitch misses by.'}

preset_dict['big_fly'] = {'tool': pyb_tools.hit_distance,
                          'flavor_columns': ['hit_distance_sc', 'launch_speed', 'launch_angle'],
                          'flavor_func': pyb_tools.home_run_flavor,
                          'description': 'Longest struck home runs.'}

preset_dict['bad_swings'] = {'tool': pyb_tools.bad_swings,
                             'flavor_columns': ['off_edge'],
                             'flavor_func': pyb_tools.ump_show_flavor,
                             'description': 'Swings and misses on pitches outside the strike zone.'}

preset_dict['worst_called_strikes'] = { 'tool': pyb_tools.worst_called_strikes,
                                        'flavor_columns': ['miss_by'],
                                        'flavor_func': pyb_tools.ump_show_flavor,
                                        'description': 'Umps calling strikes on pitches outside the strike zone.'}


preset_dict['chasing_hits'] = { 'tool': pyb_tools.chasing_hits,
                                        'flavor_columns': ['miss_by'],
                                        'flavor_func': pyb_tools.ump_show_flavor,
                                        'description': 'Batters getting hits on pitches outside the strike zone.'}

teamcodes = {"Red Sox": "BOS",
             "Yankees": "NYY",
             "Royals": "KC",
             "Reds": 'CIN', 
             "Nationals": 'WSH',
             "Rays": 'TB',
             "Marlins": 'MIA',
             "Astros": 'HOU',
             "Rangers": 'TEX',
             "Cubs": 'CHC',
             "Cardinals": 'STL',
             "Dodgers": 'LAD', 
             "Mariners": 'SEA',
             "Athletics": 'OAK',
             "Padres": 'SD',
             "Orioles": 'BAL',
             "Giants": 'SF', 
             "Twins": 'MIN', 
             "Pirates": 'PIT',
             "Braves": 'ATL',
             "Tigers": 'DET',
             "Mets": 'NYM',
             "White Sox": 'CWS', 
             "Phillies": 'PHI',
             "Brewers": 'MIL',
             "Blue Jays": 'TOR', 
             "Diamondbacks": 'AZ',
             "Guardians": 'CLE', 
             "Angels": 'LAA', 
             "Rockies": 'COL'}