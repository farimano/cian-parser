import pandas as pd
import numpy as np
import datetime


def first_preprocessing(data: pd.DataFrame) -> pd.DataFrame:
    # This function is required to delete du[licates, because search engine shows
    # the same flat several times.
    data = data.groupby(['new_object', 'room_type', 'link']).tail(1)
    return data.reset_index(drop=True)

def get_nrooms_type(row: pd.Series) -> pd.Series:
    x = row['room_type']
    if x < 6:
        return pd.Series({'n_rooms': x, 'type': 'simple'})
    if x == 6:
        return pd.Series({'n_rooms': x, 'type': 'many_rooms'})
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

def get_dt(dt_string: str) -> datetime.datetime:
    rus_month_to_num = {
        "янв":1,
        "фев":2,
        "мар":3,
        "апр":4,
        "май":5,
        "июн":6,
        "июл":7,
        "авг":8,
        "сен":9,
        "окт":10,
        "ноя":11,
        "дек":12,
    }
    
    date_str, time_str = dt_string.split(', ')
    if date_str == 'сегодня':
        date = datetime.date.today()
    elif date_str == 'вчера':
        date = datetime.date.today() - datetime.timedelta(days=1)
    else:
        month = rus_month_to_num[date_str.split()[-1]]
        day = int(date_str.split()[0])
        
        today = datetime.date.today()
        if (month, day) > (today.month, today.day):
            year = today.year - 1
        else:
            year = today.year
        date = datetime.date(year, month, day)
    time = datetime.time(*map(int, time_str.split(':')))
    
    dt = datetime.datetime.combine(date,time)
    return dt


def rename_data_columns(data: pd.DataFrame) -> None:
    col_dict = {
        'component_0': 'titles',
        'labels': 'address',
    }
    data.rename(columns=col_dict, inplace=True)