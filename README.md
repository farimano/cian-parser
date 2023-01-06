# cian-parser
The main goal of this project is to create the convenient datatool to analyse the price of real property, collecting data from popular russian site cian.ru   
  
Several snippets.
To scrap data, try this script. Also be sure to save your data in any convenient format.
```python
import pandas as pd
import numpy as np
from scraping import CianScraper

scraper = CianScraper()
scraper.start('https://kaliningrad.cian.ru/kupit-kvartiru/')
data = scraper.collect_data()
```
To make first preprocessing, use this snippet 
```python
import pandas as pd
import numpy as np
from functools import reduce
import preprocessing as prep

data_path = '...' # type your data path here
data = pd.read_csv(data_path)
df = prep.remove_duplicates(data)

funcs = [
    prep.get_post_dt, # if you do not scrap data in MSC tz, it is recommended to add the difference between your tz and msc tz 
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
In the current version for one hour you can get approximately 1600 records. Approximately 90 percent of all advertisments can be collected for small and medium -sized  cities.S
The detailed version of how this module can be used to train real estate evaluation model can be found here https://github.com/farimano/cian-parser-example  
  
In the current moment, next features can be collected:  
1) date of posting (dt)
2) address and all its components such as region, city, district, street, etc  
3) number of rooms and type of of flat as simple, many-rooms for flats with more than 6 rooms, studio and free for free planning  
4) area of flat and price for 1 squared metr  
5) maximum floor in the house and the floor of flat  
6) availability and the date of availability for new objects  
7) the description of floor  
