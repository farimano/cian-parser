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

def get_price_area(row: pd.Series) -> pd.Series:
    for i in range(6, -1, -1):
        if (row[f'component_{i}'] is not np.NaN) and ("₽" in row[f'component_{i}']):
            break
    price_col = f'component_{i}'

    raw_price, raw_price_per_metr = row[price_col].split('\n')[:2]
    price = float("".join(raw_price.split()[:-1]))
    price_per_metr = float("".join(raw_price_per_metr.split()[:-1]))

    return pd.Series({'price': price, 'area': price / price_per_metr, 'price_per_metr': price_per_metr})

def get_dt(dt_string: str, launch_date: datetime.datetime=None) -> datetime.datetime:
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
    
    launch_date = launch_date or datetime.date.today()
    
    if date_str == 'сегодня':
        date = launch_date
    elif date_str == 'вчера':
        date = launch_date - datetime.timedelta(days=1)
    else:
        month = rus_month_to_num[date_str.split()[-1]]
        day = int(date_str.split()[0])
        
        if (month, day) > (launch_date.month, launch_date.day):
            year = launch_date.year - 1
        else:
            year = launch_date.year
        date = datetime.date(year, month, day)
    time = datetime.time(*map(int, time_str.split(':')))
    
    dt = datetime.datetime.combine(date, time)
    return dt

def get_address_components(row: str) -> pd.Series:
    address = row['labels']
    comps = address.split(', ')
    
    keyword_to_val_key = {
        "р-н": "district",
        "улица": "street",
        "проезд": "street",
        "проспект": "street",
        "кв-л": "street",
        "бульвар": "street",
        "площадь": "street",
        "переулок": "street",
        "аллея": "street",
        "шоссе": "street",
        "набережная": "street",
        "тупик": "street",
        "мкр": "microdistrict",
        "ЖК": "complex",
        "пос.": "settlement",
        "ДНП": "partnership",
        "СНТ": "partnership",
        "садовое товарищество": "partnership",
        "ст.": "station",
    }
    
    vals = {'region': comps[0]}
    
    if 'округ' in comps[1]:
        vals['okrug'] = comps[1]
    else:
        vals['city'] = comps[1]
    
    remnant = []
    
    for comp in comps[2:]:
        for keyword in keyword_to_val_key:
            if comp.startswith(f"{keyword} ") or comp.endswith(f" {keyword}"):
                val_key = keyword_to_val_key[keyword]
                vals[val_key] = comp
                break
        else:
            if comp[0] in "123456789":
                vals['house_number'] = comp
            else:
                remnant.append(comp) 

    return pd.Series(vals)


def rename_data_columns(data: pd.DataFrame) -> None:
    col_dict = {
        'component_0': 'titles',
        'labels': 'address',
    }
    data.rename(columns=col_dict, inplace=True)