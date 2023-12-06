import json
import random
import time
from bs4 import BeautifulSoup
import requests


class FunBay:
    def __init__(self, url, path_to_page, path_to_data) -> None:
        self.url = url
        self.path_to_page = path_to_page
        self.path_to_data = path_to_data
    
    def get_html_page(self):
        page = requests.get(self.url).text
        with open(self.path_to_page, 'w') as f:
            f.write(page)
    
    def parse_data_to_json(self):
        with open('data/index.html', 'r') as f:
            soup = BeautifulSoup(f.read(), 'lxml') 
            result = []
            counter = 0
            for obj in soup.find_all(class_='tc-item'):
                url = obj.get("href")
                description = obj.find(class_='tc-desc-text').text
                price = obj.find(class_='tc-price').find('div').text
                data = {
                    'url': url,
                    'description': description,
                    'price': price
                }
                result.append(data)
                counter += 1
            with open(self.path_to_data, 'w') as f:
                json.dump(result, f, indent=4)

