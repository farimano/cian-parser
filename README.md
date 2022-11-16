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

df = pd.DataFrame(data)
df = prep.first_preprocessing(df)
df[['n_rooms', 'type']] = df.apply(prep.get_nrooms_type, axis=1)
df[['price', 'square', 'price_per_meter']] = df.apply(prep.get_price_square, axis=1)
prep.rename_data_columns(df)
```
In current version the time of scraping is approximately 1-2 hours. Approximately 30 percent of all advertisments can be collected.