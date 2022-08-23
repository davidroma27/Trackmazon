# For this class we need to install the following:
# - pip install BeautifulSoup
# - pip install requests

from abc import ABC, abstractmethod  # Imports ABC module
from bs4 import BeautifulSoup  # Imports scraping module
from requests_html import *
import asyncio
from config import *


# Una URL de amazon tiene la siguiente estructura (Sin parametros):
# https://www.amazon.es/realme-Smartphone-Snapdragon-Batería-SuperDart/dp/B09S6BFSX9/
# - https://www.amazon.es/ -> Dominio
# - realme-Smartphone-Snapdragon-Batería-SuperDart/ -> Titulo reducido del producto (Podemos prescindir de esta parte)
# - dp/B09S6BFSX9/ -> Identificador del producto


# Declaramos una clase abstracta para declarar los metodos necesarios para obtener datos de Amazon
# - getProductPrize(ID) -> Obtiene el precio de un producto a partir de su ID (Float)
# - getProductStock(ID) -> Obtiene el stock de un producto a partir de su ID (Boolean)

# Declaramos la clase abstracta para un producto
class Scraper(ABC):

    @abstractmethod
    def getProductPrize(self, s, url):
        pass

    @abstractmethod
    def getProductStock(self, s, url):
        pass


# Implementamos la clase abstracta
class AmzScraper(Scraper):

    # def __init__(self, url):
    #     # self.proxies = getWorkingProxies()  # Proxies para realizar las peticiones
    #     # self.proxy = random.choice(tuple(self.proxies))  # Escogemos un proxy aleatorio de la lista
    #     # self.proxy = '113.65.20.81:9797'
    #     self.headers = {
    #         'user-agent': useragent,
    #         'accept': accept,
    #         'accept-encoding': acceptenc,
    #         'accept-language': acceptlang,
    #         'cache-control': cachecon
    #     }
    #     # self.request = requests.get(url, self.headers, proxies={ "http": self.proxy, "https": self.proxy }, timeout=5)
    #     self.request = requests.get(url, self.headers, timeout=5)

    # def __init__(self, url):
    #     # Crea una sesion HTML
    #     self.session = AsyncHTMLSession()
    #     self.response = self.session.get(url) # Se pasa la URL del producto a rastrear
    #     self.response.html.render(sleep=1) # Espera a que renderice la pagina

    # Rastrea un producto que NO TIENE STOCK
    async def getProductStock(self, s, url):
        # soup = BeautifulSoup(self.response.text, 'html.parser')
        # stock = soup.find('span', class_='a-size-medium a-color-success').text

        # Crea una sesion HTML
        # session = AsyncHTMLSession()
        response = await s.get(url) # Se pasa la URL del producto a rastrear
        await response.html.arender(sleep=1) # Espera a que renderice la pagina


        try:
            stock = response.html.find('span.a-size-medium, a-color-success', first=True).text
            if stock == '':
                stock = response.html.find('span.a-size-medium, a-color-state', first=True).text
            else:
                pass
        except:
            stock = '' # Devuelve vacío cuando el producto no muestra información de stock
        return stock

    # Rastrea el PRECIO de un producto que tiene stock
    async def getProductPrize(self, s, url):
        # soup = BeautifulSoup(self.request.text, 'html.parser')
        # prize = soup.select("span.a-offscreen")
        response = await s.get(url) # Se pasa la URL del producto a rastrear
        await response.html.arender(sleep=1) # Espera a que renderice la pagina

        try:
            prize = response.html.find('span.a-offscreen')[0].text
        except:
            prize = response.html.find('span.a-size-medium, a-color-price, header-price, a-text-normal')[0].text
        return prize


    #Metodo main que gestiona las peticiones de forma asincrona mediante tareas. Dos parametros:
    # url: La url a la que se realiza la peticion
    # action : Se indica la accion a realizar para llamar al metodo necesario
    async def main(self, url, action):
        global task
        s = AsyncHTMLSession()
        if action == 'stock':
            task = self.getProductStock(s, url)
        if action == 'precio':
            task = self.getProductPrize(s, url)

        return await asyncio.gather(task)

# if __name__ == "__main__":
# #     # getProxies()
#     amz = AmzScraper('https://www.amazon.es/Building-Scalable-Data-Warehouse-Vault/dp/0128025107/')
#     print(amz.getProductPrize())