import get_vid
import pyb_tools

def make_highlight_reel(start_date, end_date, n_highlights, format, daily = False):
    df = pyb_tools.get_statcast_data(start_date, end_date)
    df = preset_dict[format]['tool'](df)
    if daily:
        df_replacement = pyb_tools.pd.DataFrame(columns = df.columns)
        for date in df['game_date'].unique():
            df_temp = df.loc[df['game_date'] == date].head(n_highlights)
            df_replacement = pyb_tools.pd.concat([df_replacement, df_temp])
        df = df_replacement.sort_values(by = 'game_date', ascending = True)
    else:
        df = df.head(n_highlights)
    df['flavor'] = df[preset_dict[format]['flavor_column']].apply(preset_dict[format]['flavor_func'])
    args = pyb_tools.get_search_args_list(df)
    captions = pyb_tools.generate_captions(args, list(df['flavor']))
    print(captions)
    compilation = get_vid.create_compilation_from_args(args, captions = captions)

preset_dict = {}
preset_dict['ump_show'] = {'tool': pyb_tools.ump_show,
                           'flavor_column': 'miss_by',
                           'flavor_func': pyb_tools.ump_show_flavor}

preset_dict['called_corners'] = {'tool': pyb_tools.called_corners,
                                 'flavor_column': 'off_center',
                                 'flavor_func': lambda x: ''}

preset_dict['clutch'] = {'tool': pyb_tools.clutch,
                         'flavor_column': 'delta_win_exp',
                         'flavor_func': pyb_tools.clutch_flavor}