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

    return output

def kzone_miss(df):
    """Takes in a statcast dataframe and calculates the distance the pitch misses the strike zone."""

    correction = 0.15

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

    df['high_low'] = df[['sz_top', 'sz_bot', 'plate_z']].apply(ft_high_or_low, axis = 1)
    df['off_edge'] = df['plate_x'].apply(off_edge)
    df['miss_by'] = df[['high_low', 'off_edge']].apply(miss_by, axis = 1)

    return df

def off_center(df):

    def calc_off_center(x):
        plate_x, plate_z, sz_top, sz_bot = x
        a = plate_x
        b = plate_z - ((sz_top + sz_bot)/2)
        c = (a * a) + (b * b)
        return c ** 0.5
    
    df['off_center'] = df[['plate_x', 'plate_z', 'sz_top', 'sz_bot']].apply(calc_off_center, axis = 1)
    return df


def worst_called_strikes(df):
    """Takes in a statcast dataframe, filters for called strikes, and sorts by the most egregious called strikes."""
    df = df.dropna(subset = ['sz_top', 'sz_bot', 'plate_x' , 'plate_z'])
    df = df.loc[df['description'] == 'called_strike']
    df = kzone_miss(df)
    df = df.sort_values(by = 'miss_by', ascending = False)
    return df

def worst_called_balls(df):
    """Takes in a statcast dataframe, filters for called strikes, and sorts by the most egregious called balls."""
    df = df.dropna(subset = ['sz_top', 'sz_bot', 'plate_x' , 'plate_z'])
    df = df.loc[df['description'] == 'ball']
    df = off_center(df)
    df = df.sort_values(by = 'off_center', ascending = True)
    return df
