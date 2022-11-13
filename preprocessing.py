import pandas as pd
import numpy as np

def get_price_square(row: pd.Series) -> pd.Series:
    for i in range(6, -1, -1):
        if (row[f'component_{i}'] is not np.NaN) and ("₽" in row[f'component_{i}']):
            break
    price_col = f'component_{i}'

    raw_price, raw_price_per_metr = row[price_col].split('\n')[:2]
    price = float("".join(raw_price.split()[:-1]))
    price_per_metr = float("".join(raw_price_per_metr.split()[:-1]))

    return pd.Series({'price': price, 'square': price / price_per_metr, 'price_per_metr': price_per_metr})