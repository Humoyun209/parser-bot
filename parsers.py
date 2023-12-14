import json
from bs4 import BeautifulSoup
import aiohttp
import aiofiles


class FunBay:
    def __init__(self, url, path_to_page, path_to_data) -> None:
        self.url = url
        self.path_to_page = path_to_page
        self.path_to_data = path_to_data
    
    async def get_html_page(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                result = await response.text()
                async with aiofiles.open(self.path_to_page, 'w', encoding='utf-8') as f:
                    await f.write(result)
    
    async def parse_data_to_json(self):
        async with aiofiles.open('data/index.html', 'r', encoding="utf-8") as f:
            soup = BeautifulSoup(await f.read(), 'lxml') 
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
            async with aiofiles.open(self.path_to_data, 'w', encoding="utf-8") as f:
                await f.write(json.dumps(result, indent=4))
