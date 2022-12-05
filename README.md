# cian-parser
This main goal of this project is to create the convenient datatool to analyse the price of real property, collecting data from popular russian site cian.ru   
  
Example of how this module can be used:  
```python
import pandas as pd
import numpy as np
from functools import reduce
from scraping import CianScraper

import preprocessing as prep

scraper = CianScraper()
scraper.start('https://kaliningrad.cian.ru/kupit-kvartiru/')
data = scraper.collect_data()

df = pd.DataFrame(data)
df = prep.first_preprocessing(df)
df['dt'] = df['dt'].map(prep.get_dt)

funcs = [
    prep.get_nrooms_type,
    prep.get_price_area,
    prep.get_address_components,
    prep.get_cian_description,
    prep.get_availability,
    prep.get_floors,
]
df = reduce(lambda x, y: x.join(x.apply(y, axis=1)), [df, *funcs])
prep.rename_drop_columns(df)
```
In current version the time of scraping is approximately 12 hours. Approximately 90 percent of all advertisments can be collected.  
  
In the current moment, next features can be collected:  
1) date of posting (dt)
2) address and all its components such as region, city, district, street, etc  
3) number of rooms and type of of flat as simple, many-rooms for flats with more than 6 rooms, studio and free for free planning  
4) area of flat and price for 1 squared metr  
5) maximum floor in the house and the floor of flat  
6) availability and the date of availability for new objects  
7) the description of floor  