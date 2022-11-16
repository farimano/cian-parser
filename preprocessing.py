import pandas as pd
import numpy as np


def first_preprocessing(data: pd.DataFrame) -> pd.DataFrame:
    # this function is required to delete du[licates, saving the more earlier appearance among all segments
    # this transformation will be removed after the process of scraping will be adjusted
    data['count_room_type'] = data.groupby(['room_type', 'new_object']).cumcount()
    max_count = (
        data
        .groupby(['room_type', 'new_object'])
        .agg(max_count=('count_room_type', lambda x: x.max() + 1))
        .reset_index()
    )

    data = data.merge(max_count, on=['room_type', 'new_object'], how='left')
    data['count_room_type'] = data['count_room_type'] - data['max_count']
    data = data.sort_values('count_room_type').groupby('link').head(1)
    data.drop(['count_room_type', 'max_count'], axis=1, inplace=True)
    return data.reset_index(drop=True)

def get_nrooms_type(row: pd.Series) -> pd.Series:
    x = row['room_type']
    if x <= 6:
        return pd.Series({'n_rooms': x, 'type': 'simple'})
    if x == 7:
        return pd.Series({'n_rooms': 1, 'type': 'free'})
    if x == 9:
        return pd.Series({'n_rooms': 1, 'type': 'studio'})

def get_price_square(row: pd.Series) -> pd.Series:
    for i in range(6, -1, -1):
        if (row[f'component_{i}'] is not np.NaN) and ("₽" in row[f'component_{i}']):
            break
    price_col = f'component_{i}'

    raw_price, raw_price_per_metr = row[price_col].split('\n')[:2]
    price = float("".join(raw_price.split()[:-1]))
    price_per_metr = float("".join(raw_price_per_metr.split()[:-1]))

    return pd.Series({'price': price, 'square': price / price_per_metr, 'price_per_metr': price_per_metr})

def rename_data_columns(data: pd.DataFrame) -> None:
    col_dict = {
        'component_0': 'titles',
        'labels': 'address',
    }
    data.rename(columns=col_dict, inplace=True)