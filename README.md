# cian-parser
cian-parser is a tool for analyzing the prices of real estate properties, using data collected from the Russian website cian.ru.

## Features
- Scrape data using the `CianScraper` class
- Perform initial preprocessing on the data using the `preprocessing` module
- Collect the following data points:
  - Date of posting
  - Address and its components (region, city, district, street, etc.)
  - Number of rooms and type of flat (simple, many-rooms for flats with more than 6 rooms, studio, or free for free planning)
  - Area of flat and price per square meter
  - Maximum floor in the building and the floor of the flat
  - Availability and availability date for new properties
  - Description of the flat

## Usage
To scrape data, use the following script:

```python
import pandas as pd
from scraping import CianScraper

scraper = CianScraper()
scraper.start('https://kaliningrad.cian.ru/kupit-kvartiru/')
data = scraper.collect_data()
```
To perform initial preprocessing on the data:  
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
##Notes
  - In the current version, approximately 1600 records can be collected in an hour.
  - For small and medium-sized cities, approximately 90% of all advertisements can be collected.
  - For more information on using this module to train a real estate evaluation model, see this https://github.com/farimano/cian-parser-example  
