# cian-parser
This main goal of this project is to create the convenient datatool to analyse the price of real property, collecting data from popular russian site cian.ru   
  
Example of how this module can be used:  
```python
from scraping import CianScraper
import preprocessing as prep
import pandas as pd

scraper = CianScraper()
scraper.start('https://kaliningrad.cian.ru/kupit-kvartiru/')
data = scraper.collect_data()

data = pd.DataFrame(data)
data = prep.first_preprocessing(data)
data[['n_rooms', 'type']] = data.apply(prep.get_nrooms_type, axis=1)
data[['price', 'square', 'price_per_meter']] = data.apply(prep.get_price_square, axis=1)
data['dt'] = data['dt'].map(prep.get_dt)
prep.rename_data_columns(data)
data.drop(['room_type'], axis=1, inplace=True)
```
In current version the time of scraping is approximately 1-2 hours. Approximately 50 percent of all advertisments can be collected because some similar ads are representet by one flat.