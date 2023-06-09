# Additional tools to work with pybaseball
import pybaseball
import datetime
import pandas as pd

def get_statcast_data(start_date = '2023-03-30', end_date = (datetime.date.today() - datetime.timedelta(days = 2)).__str__()) -> pd.DataFrame:
    """Pulls statcast data for the specified timeframe and returns it as a pd.DataFrame. Dates default to the beginning of the 2023 season to yesterday."""
    data = pybaseball.statcast(start_dt = start_date, end_dt = end_date).reset_index(drop = True)
    return data

def get_search_args(s: pd.Series) -> dict:
    """Takes an entry in a pybaseball-generated DataFrame and extracts the data for search."""
    output = {}
    output['batter'] = s['batter']
    output['pitcher'] = s['pitcher']
    output['date'] = str(s['game_date'])[:10]
    output['inning'] = s['inning']
    output['balls'] = s['balls']
    output['strikes'] = s['strikes']
    output['result'] = s['description']
    output['home_team'] = s['home_team']
    output['batter'] = s['batter']
    output['pitcher'] = s['pitcher']
    output['topbot'] = s['inning_topbot']

    return output

def get_search_args_list(df) -> list:
    """Takes a statcast dataframe and returns the list of args needed to get the URL."""
    output = []
    for i in range(len(df)):
        output.append(get_search_args(df.iloc[i]))
    return output


def generate_caption(n, pitcherid, batterid, date, flavor = ''):
    """Generates a caption for a compilation."""
    df = pybaseball.playerid_reverse_lookup([pitcherid])
    pitcher = df.loc[0, 'name_first'].title() + ' ' + df.loc[0, 'name_last'].title()
    df = pybaseball.playerid_reverse_lookup([batterid])
    batter = df.loc[0, 'name_first'].title() + ' ' + df.loc[0, 'name_last'].title()
    if len(flavor) > 0:
        flavor = ', ' + flavor
    output = f'{n}) {date} {pitcher} to {batter}{flavor}'
    return output

def generate_captions(argslist, flavorlist = None):
    """Generates mutliple captions for a compilation."""
    if flavorlist == None:
        flavorlist = [''] * len(argslist)
    output = []
    for i, args in enumerate(argslist):
        output.append(generate_caption(i + 1, args['pitcher'], args['batter'], args['date'], flavorlist[i]))
    return output

def cols_in_group(x, group):
    a = x[0]
    b = x[1]
    return (a in group) or (b in group)

def kzone_miss(df):
    """Takes in a statcast dataframe and calculates the distance the pitch misses the strike zone."""

    correction = 0.3

    def ft_high_or_low(x):
        sz_top, sz_bot, plate_z = x
        if (plate_z > sz_bot - correction) and (plate_z < sz_top + correction):
            return 0
        return min(abs(sz_bot - plate_z + correction), abs(plate_z - sz_top - correction))

    def off_edge(x):
        if (x > -0.75) and (x < 0.75):
            return 0
        else:
            return abs(x) - 0.75

    def miss_by(x):
        a, b = x
        return round(((a * a) + (b * b)) ** 0.5, ndigits = 2)

    df = df.dropna(subset = ['sz_top', 'sz_bot', 'plate_z', 'plate_x'])

    df['high_low'] = df[['sz_top', 'sz_bot', 'plate_z']].apply(ft_high_or_low, axis = 1)
    df['off_edge'] = df['plate_x'].apply(off_edge)
    df['miss_by'] = df[['high_low', 'off_edge']].apply(miss_by, axis = 1)

    return df

def batted_balls(df, teams):
    """Filters a dataframe to only include balls hit in play."""
    df = df.loc[df['description'] == 'hit_into_play']
    if len(teams) > 0:
        df = df.loc[df['home_team'].apply(lambda x: x in teams) == df['inning_topbot'].apply(lambda x: x == 'Bot')]
    return df


def off_center(df):
    """Calculates the distance from the pitch's arrival point from the center of the strike zone"""

    def calc_off_center(x):
        plate_x, plate_z, sz_top, sz_bot = x
        a = plate_x
        b = plate_z - ((sz_top + sz_bot)/2)
        c = (a * a) + (b * b)
        return c ** 0.5
    
    df['off_center'] = df[['plate_x', 'plate_z', 'sz_top', 'sz_bot']].apply(calc_off_center, axis = 1)
    return df


def worst_called_strikes(df, teams, players):
    """Takes in a statcast dataframe, filters for called strikes, and sorts by the most egregious called strikes."""
    df = df.dropna(subset = ['sz_top', 'sz_bot', 'plate_x' , 'plate_z'])
    df = df.loc[df['description'] == 'called_strike']
    df = kzone_miss(df)
    if len(teams) > 0:
        df = df.loc[df['home_team'].apply(lambda x: x in teams) == df['inning_topbot'].apply(lambda x: x == 'Bot')]
    df = df.sort_values(by = 'miss_by', ascending = False)
    return df

def worst_called_balls(df, teams, players):
    """Takes in a statcast dataframe, filters for called balls, and sorts by the most egregious called balls."""
    df = df.dropna(subset = ['sz_top', 'sz_bot', 'plate_x' , 'plate_z'])
    df = df.loc[df['description'] == 'ball']
    df = off_center(df)
    if len(teams) > 0:
        df = df.loc[df['home_team'].apply(lambda x: x in teams) == df['inning_topbot'].apply(lambda x: x == 'Bot')]
    df['off_center'] = df['off_center'].apply(lambda x: -x)
    df = df.sort_values(by = 'off_center', ascending = False)
    return df

def scorchers(df, teams, players):
    """Takes in a Statcast dataframe, sorts by hard contact with a positive launch angle."""
    df = batted_balls(df, teams)
    df = df.loc[df['launch_angle'] > 0]
    return df

def undergrounders(df, teams, players):
    """Takes in a Statcast dataframe, sorts by hard contact with a launch angle below -10."""
    df = batted_balls(df, teams)
    df = df.loc[df['launch_angle'] < -10]
    return df

def takes_of_steel(df, teams, players):
    """Takes in a Statcast dataframe, filters for 2-strike takes that result in a ball, sorted by proximity to the strie zone."""
    df = worst_called_balls(df, teams, players)
    df = df.loc[df['strikes'] == 2]
    return df

def called_corners(df, teams, players):
    """Takes in a statcast dataframe, filters for correctly called strikes far from the center of the strike zone."""
    df = df.dropna(subset = ['sz_top', 'sz_bot', 'plate_x' , 'plate_z'])
    df = df.loc[df['description'] == 'called_strike']
    df = kzone_miss(df)
    df = df.loc[df['miss_by'] == 0]
    df = off_center(df)
    if len(teams) > 0:
        df = df.loc[df['home_team'].apply(lambda x: x in teams) == df['inning_topbot'].apply(lambda x: x == 'Top')]
    df = df.sort_values(by = 'off_center', ascending = False)
    return df

def ump_show(df, teams, players):
    """Takes in a statcast dataframe, and filters for umps ringing up batters on pitches outside the strike zone."""
    df = worst_called_strikes(df, teams, players)
    df = df.loc[df['strikes'] == 2]
    return df

def ump_show_flavor(x):
    """Generates flavor text for ump show from the 'miss_by' column."""
    return f'miss by {x[0] * 12:.1f} inches'

def clutch(df, teams, players):
    """Takes in a statcast dataframe, then finds the most impactful moments by WPA."""
    
    def topbot(x):
        if x == 'Top':
            return 1
        else:
            return -1

    def in_group(x):
        if x in group:
            return 1
        else:
            return -1

    if len(teams) + len(players) == 0:
        df['delta_win_exp'] = df['delta_home_win_exp'].apply(abs)
    else:
        if len(teams) > 0:
            group = teams
            df['in_group'] = df['home_team'].apply(in_group)
            df['delta_win_exp'] = df['delta_home_win_exp'] * df['in_group']
        else:
            group = players
            df['topbot'] = df['inning_topbot'].apply(topbot)
            df['in_group'] = df['pitcher'].apply(in_group)
            df['delta_win_exp'] = df['delta_home_win_exp'] * df['topbot'] * df['in_group']
    return df.sort_values(by = 'delta_win_exp', ascending = False)


def clutch_flavor(x):
    """Generates flavor text for clutch from the 'delta_win_exp' column."""
    return f'{x[0]} change in WPA'

def batted_ball_flavor(x):
    """Generates flavor text describing batted ball data."""
    return f'{x[0]} MPH, {x[1]:.0f} degrees'

def walks(df, teams, players):
    """Takes in a Statcast dataframe, filters it for balls that result in a walk, and sorts by the miss margin."""
    df = kzone_miss(df)
    df = df.loc[df['description'] == 'ball']
    df = df.loc[df['balls'] == 3]
    return df

def full_count_walks(df, teams, players):
    """Takes in a Statcast dataframe, filters it for balls that result in a walk on 3-2 counts, and sorts by the miss margin."""
    df = walks(df, teams, players)
    df = df.loc[df['strikes'] == 2]
    return df
