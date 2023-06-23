import aiohttp
from bs4 import BeautifulSoup

url23 = 'https://etnosvit.com/uk/anekdoty_uk.html'


async def parse_jokes():
    async with aiohttp.ClientSession() as session:
        async with session.get(url23) as response:
            soup = BeautifulSoup(await response.text(), 'html.parser')
    jokes = soup.find_all('div', class_='sue-panel-content sue-content-wrap')
    return [joke.get_text() for joke in jokes]
