import pandas as pd
import numpy as np

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

import time


class RandomTimeEvents:
    @staticmethod
    def sleep(s: float):
        rnd_append = abs(np.random.randn())
        time.sleep(s+rnd_append)        

class CianParser:
 
    def __init__(self):
        options = Options()
        options.add_argument("start-maximized")
        chrome_servise = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=chrome_servise, options=options)
        
        self.pagination = True
        self.more_button = True
    
    def start(self, link: str):
        self._get_link(link)
        buttons = self.driver.find_elements(By.CSS_SELECTOR, value='button')
        accept_button, = list(filter(lambda x: "принять" in x.text.lower(), buttons))
        accept_button.click()
    
    def _get_link(self, link: str):
        self.driver.get(link)
        RandomTimeEvents.sleep(5)
    
    def collect_data(self):
        self.data = []
        self.total = int(''.join(self.driver.find_element(By.XPATH, "//div[@data-name='SummaryHeader']").text.split()[1:-1]))
        self.preprocessed = 0
        
        while self.pagination:
            self._collect_data_by_pagination()
        
        while self.more_button:
            self._collect_data_by_more_button()
        
        self._parse_data()
        self.driver.close()
        return self.data
    
    def _collect_data_by_pagination(self):
        RandomTimeEvents.sleep(5)

        
        page_section, = self.driver.find_elements(By.XPATH, "//div[@data-name='Pagination']")
        pages = (page for page in page_section.find_elements(By.XPATH, ".//li"))
        active_pass = False
        while not active_pass:
            if 'active' in next(pages).get_attribute('class'):
                active_pass = True
        try:
            next_page = next(pages)
            next_link = next_page.find_element(By.XPATH, './/a').get_attribute('href')
            self._parse_data()
            self._get_link(next_link)
        except StopIteration:
            self.pagination = False
    
    def _collect_data_by_more_button(self):
        RandomTimeEvents.sleep(5)
        try:
            more_button, = self.driver.find_elements(By.XPATH, "//a[contains(@class, 'more-button')]")
            more_button.click()
        except ValueError:
            self.more_button = False
    
    def _parse_data(self):
        new_data = []
        articles = self.driver.find_elements(By.XPATH, '//article')
        for article in articles:
            art_dict = {}
            
            try:
                art_dict['link'] = article.find_element(By.XPATH, ".//a[contains(@href,'cian.ru/sale/flat')]").get_attribute('href')
                art_dict['is_new_home'] = bool(
                    list(
                        filter(
                            lambda x: True if "новостройка" in x.text.lower() else False, 
                            article.find_elements(By.XPATH, ".//div[contains(@class, 'black-label')]")
                        )
                    )
                )

                art_dict['offer_title'] = article.find_element(By.XPATH, ".//span[@data-mark='OfferTitle']").text
                art_dict['labels'] = article.find_element(By.XPATH, ".//div[contains(@class, 'labels')]").text

                components = article.find_elements(By.XPATH, ".//div[@data-name='GeneralInfoSectionRowComponent']")
                
                for num, component in enumerate(components):
                    art_dict[f'component_{num}'] = component.text
                
                art_dict['dt'] = article.find_element(By.XPATH, ".//div[@data-name='TimeLabel']//div[contains(@class,'absolute')]//span").get_attribute('innerHTML')
                art_dict['subtitle'] = article.find_element(By.XPATH, ".//div[contains(@class, 'subtitle')]").text
                art_dict['html_source'] = article.get_attribute('innerHTML')
            except:
                art_dict['html_source'] = article.get_attribute('innerHTML')
            
            new_data.append(art_dict)        
        
        self.data.extend(new_data)
        self.preprocessed += len(new_data)
        print(f"{self.preprocessed}\t/\t{self.total} ({self.preprocessed/self.total:.2%})")