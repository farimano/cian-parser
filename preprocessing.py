import pandas as pd
import numpy as np
import datetime


def remove_duplicates(data: pd.DataFrame) -> pd.DataFrame:
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
        if not(pd.isna(row[f'component_{i}'])) and ("₽" in row[f'component_{i}']):
            break
    price_col = f'component_{i}'

    raw_price, raw_price_per_metr = row[price_col].split('\n')[:2]
    price = float("".join(raw_price.split()[:-1]))
    price_per_metr = float("".join(raw_price_per_metr.split()[:-1]))

    return pd.Series({'price': price, 'area': price / price_per_metr, 'price_per_metr': price_per_metr})

def get_post_dt(row: pd.Series, msc_tz_diff: int=0) -> datetime.datetime:
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
    
    dt_string = row['dt']
    date_str, time_str = dt_string.split(', ')
    time = datetime.time(*map(int, time_str.split(':')))
    
    launch_dt = datetime.datetime.fromisoformat(row['cur_datetime'])-datetime.timedelta(hours=msc_tz_diff)
    launch_date = launch_dt.date()
    
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
   
    dt = datetime.datetime.combine(date, time)
    return pd.Series({'post_dt': dt})

def get_address_components(row: pd.Series, debug=False) -> pd.Series:
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
        "м.": 'underground',
        "мкр.": 'microdistrict',
        "район": "district",
        "д.": 'hamlet',
        "с/пос": "settlement",
        "с.": "village",
        "микрорайон": "microdistrict",
        "жилмассив": "complex",
        "тракт": "street",
        "cельское поселение": "settlement",
        "тер.": "street",
        "городок": "street",
    }
    
    replace_val_dict = {
        "МЖК": "complex",
        "уч9": "ignore",
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
                house_number = comp
                int_house_number = "".join([sym if sym.isdigit() else '|' for sym in house_number]).split('|', 1)[0]
                int_house_number = int(int_house_number)
                
                vals['house_number'] = house_number
                vals['int_house_number'] = int_house_number
            elif comp[0] in "кс":
                pass
            elif comp in replace_val_dict:
                vals[replace_val_dict[comp]] = comp
            else:
                remnant.append(comp)
    if debug:
        if remnant:
            print(remnant)
    return pd.Series(vals)

def get_floors(row: pd.Series) -> pd.Series:
    title, subtitle = row[['offer_title', 'subtitle']]
    
    for element in [title, subtitle]:
        if ('этаж' in str(element)) and (len(element.split(', ')) == 3):
            floor, max_floor = element.split(', ')[2][:-5].split('/')
            return pd.Series({'floor': floor, 'max_floor': max_floor}).map(int)
    return pd.Series({'floor': None, 'max_floor': None})

def get_availability(row: pd.Series) -> pd.Series:
    row = row['subtitle']
    if pd.isna(row):
        return pd.Series({'is_available': None, 'available_date': None})
    elif 'Сдан' in row:
        return pd.Series({'is_available': 1, 'available_date': None})
    elif 'Сдача корпуса' in row:
        av_date = row.split('корпуса ')[-1].split()
        quart = int(av_date[0])
        year = int(av_date[2])
        date = datetime.date(year, 1, 1) + datetime.timedelta(45 + 90 * (quart-1))
        return pd.Series({'is_available': 0, 'available_date': date})

def get_cian_description(row: pd.Series) -> pd.Series:
    description_components = row[['component_3', 'component_4']].fillna('₽/м²')
    not_price_components = list(filter(lambda x: not ("₽/м²" in x), description_components))
    if not_price_components:
        return pd.Series({'cian_description': not_price_components[0]})
    else:
        return pd.Series({"cian_description": None})

def rename_drop_columns(data: pd.DataFrame) -> None:
    col_dict = {
        'labels': 'address',
    }
    data.rename(columns=col_dict, inplace=True)
    
    comp_cols = [col for col in data if col.startswith('component')]
    drop_cols = [
        *comp_cols,
        'offer_title',
        'subtitle',
        'room_type',
        'dt',
        'cur_datetime',
        'ignore',
        'min_price',
        'max_price',
    ]
    data.drop([col for col in drop_cols if col in data.columns], axis=1, inplace=True)