import get_vid
import pyb_tools

def make_highlight_reel(start_date, end_date, n_highlights, format, daily = False, teams = [], players = [],
                        ascending = False):
    df = make_leaderboard(start_date, end_date, n_highlights, format, daily, teams, players, ascending)
    df['flavor'] = df[preset_dict[format]['flavor_column']].apply(preset_dict[format]['flavor_func'])
    args = pyb_tools.get_search_args_list(df)
    captions = pyb_tools.generate_captions(args, list(df['flavor']))
    print(captions)
    compilation = get_vid.create_compilation_from_args(args, captions = captions)

def make_leaderboard(start_date, end_date, n_highlights, format, daily = False, teams = [], players = [],
                     ascending = False):
    df = pyb_tools.get_statcast_data(start_date, end_date)
    # Next line calls a function from a dict
    df = preset_dict[format]['tool'](df, teams, players)
    df = df.sort_values(by = preset_dict[format]['flavor_column'], ascending = ascending)
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
                           'flavor_column': 'miss_by',
                           'flavor_func': pyb_tools.ump_show_flavor,}

preset_dict['called_corners'] = {'tool': pyb_tools.called_corners,
                                 'flavor_column': 'off_center',
                                 'flavor_func': lambda x: '',}

preset_dict['clutch'] = {'tool': pyb_tools.clutch,
                         'flavor_column': 'delta_win_exp',
                         'flavor_func': pyb_tools.clutch_flavor,}

preset_dict['blind_umps'] = {'tool': pyb_tools.worst_called_balls,
                             'flavor_column': 'off_center',
                             'flavor_func': lambda x: ''}


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