import pandas as pd
import numpy as np

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from preprocessing import get_price_area

import time
import datetime


class RandomTimeEvents:
    @staticmethod
    def sleep(s: float):
        rnd_append = abs(np.random.randn())
        time.sleep(s+rnd_append)        

class CianScraper:
 
    def __init__(self):
        options = Options()
        options.add_argument("start-maximized")
        chrome_servise = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=chrome_servise, options=options)
    
    def start(self, link: str):
        self._get_link(link)
        self._accept_cookies()
        
        self.total = self._get_total_count()
        self.preprocessed = 0
        
        reg_link = self.driver.find_elements(By.XPATH, "//div[@data-name='Pagination']//a[@href]")[1].get_attribute('href')
        self.region = dict(map(lambda x: x.split('='), reg_link.split('?')[1].split('&')))['region']
        
        self.data = []
    
    def _get_link(self, link: str):
        self.driver.get(link)
        RandomTimeEvents.sleep(5)
    
    def _accept_cookies(self):
        buttons = self.driver.find_elements(By.CSS_SELECTOR, value='button')
        accept_button, = list(filter(lambda x: "принять" in x.text.lower(), buttons))
        accept_button.click()
        
    def _get_total_count(self):
        return int(
            ''.join(
                self.driver
                .find_element(By.XPATH, "//div[@data-name='SummaryHeader']")
                .text.split()[1:-1]
            )
        )
    
    def collect_data(self):
        segments = []
        for room_type in range(1, 10):
            if room_type != 8:
                for new_object in [True, False]:
                    segments.append({'new_object': new_object, 'room_type': room_type})
        self.segments = segments
        while self.segments:
            self.segment = self.segments.pop(0)
            self._collect_data_by_segment(self.segment)
        print('The process has been completed!')
        self.driver.close()
        
        return self.data
    
    def collect_data_by_segments(self, segments):
        self.segments = segments
        while self.segments:
            self.segment = self.segments.pop(0)
            self._collect_data_by_segment(self.segment)
        print('The process has been completed!')
        self.driver.close()
        
        return self.data
    
    def _collect_data_by_segment(self, segment):
        segment_link = self._generate_cian_link_for_segment(**segment)
        RandomTimeEvents.sleep(30)
        self._get_link(segment_link)
        
        price_segments = [{**segment}]
        if not segment['new_object']:
            article_num = self._get_total_count()
            n_price_segments = article_num / 1500
            n_quantiles = int((n_price_segments // 1) + bool(n_price_segments % 1))
            
            if n_quantiles >= 2:
                price_list = self._get_price_list(segment, n_quantiles)
                price_segments = [
                    {'min_price':price_list[i], 'max_price':price_list[i+1], **segment} 
                    for i in range(len(price_list) - 1)
                ]
        for segment in price_segments:
            segment_link = self._generate_cian_link_for_segment(**segment)
            self.similar_links = []

            RandomTimeEvents.sleep(30)
            self._get_link(segment_link)
            self._collect_data(segment)

            self.similar_links = list(set(self.similar_links))

            for similar_link in self.similar_links:
                RandomTimeEvents.sleep(5)
                self._get_link(similar_link)
                self._collect_data(segment)

            segment_string = ", ".join([f"{key}-{val}" for key, val in segment.items()])
            print(f'\nSegment {segment_string} has been preprocessed!')
    
    def _collect_data(self, segment):
        self.pagination = True
        
        while self.pagination:
            self._collect_data_by_pagination(segment)
        
        self._scrap_data(segment)
    
    def _get_price_list(self, segment, n_quantiles):
        quantiles = [(i+1) / n_quantiles for i in range(n_quantiles-1)]
        room_type = segment['room_type']
        data = pd.DataFrame(self.data)
        data = data[data['room_type']==room_type]
        price = data.apply(get_price_area, axis=1)['price']
        
        q_price = [price.quantile(q) for q in quantiles]
        adj_q_price = [price / 2 for price in q_price]
        q_price.extend(adj_q_price)
        q_price = [int(price) for price in q_price]
        q_price.sort()
        
        price_list = [None, *q_price, None]
        return price_list
        
    
    def _generate_cian_link_for_segment(self, room_type, new_object, min_price=None, max_price=None):
        link = 'https://cian.ru/cat.php?currency=2&deal_type=sale&engine_version=2'
        if max_price is not None:
            link = link + f"&maxprice={max_price}"
        if min_price is not None:
            link = link + f"&minprice={min_price}"
        link = link + f'&object_type%5B0%5D={new_object+1}&offer_type=flat&region={self.region}'
        link = link + f'&room{room_type}=1'
        return link
    
    def _collect_data_by_pagination(self, segment):
        RandomTimeEvents.sleep(5)
        
        all_pages = self.driver.find_elements(By.XPATH, "//div[@data-name='Pagination']//li")
        pages = (page for page in all_pages)
        active_pass = not bool(all_pages)
        while not active_pass:
            if 'active' in next(pages).get_attribute('class'):
                active_pass = True
        try:
            next_page = next(pages)
            next_link = next_page.find_element(By.XPATH, './/a').get_attribute('href')
            self._scrap_data(segment)
            self._get_link(next_link)
        except StopIteration:
            self.pagination = False
    
    def _scrap_data(self, segment):
        new_data = []
        all_articles = self.driver.find_elements(By.XPATH, '//article')
        suggestion_articles = self.driver.find_elements(By.XPATH, '//div[@data-name="Suggestions"]//article')
        
        articles = list(set(all_articles).difference(set(suggestion_articles)))
        
        for article in articles:
            art_dict = {**segment}
            art_dict['cur_datetime'] = datetime.datetime.now()
            
            art_dict['link'] = article.find_element(By.XPATH, ".//a[contains(@href,'cian.ru/sale/flat')]").get_attribute('href')

            art_dict['offer_title'] = article.find_element(By.XPATH, ".//span[@data-mark='OfferTitle']").text
            art_dict['labels'] = article.find_element(By.XPATH, ".//div[contains(@class, 'labels')]").text

            components = article.find_elements(By.XPATH, ".//div[@data-name='GeneralInfoSectionRowComponent']")

            for num, component in enumerate(components):
                art_dict[f'component_{num}'] = component.text
                if component.text.startswith('Ещё'):
                    sim_link_list = component.find_elements(By.XPATH, './/a[@href]')
                    if sim_link_list:
                        self.similar_links.append(sim_link_list[0].get_attribute('href'))
                    

            art_dict['dt'] = article.find_element(By.XPATH, ".//div[@data-name='TimeLabel']//div[contains(@class,'absolute')]//span").get_attribute('innerHTML')

            subtitles = article.find_elements(By.XPATH, ".//div[contains(@class, 'subtitle')]")
            if subtitles:
                art_dict['subtitle'] = subtitles[0].text
            
            new_data.append(art_dict)        
        
        self.data.extend(new_data)
        self.preprocessed += len(new_data)
        print(f"{self.preprocessed}\t/\t{self.total} ({self.preprocessed/self.total:.2%})", end='\r')