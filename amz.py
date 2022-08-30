from abc import ABC, abstractmethod  # Imports ABC module
from requests_html import *
import asyncio

#  Declaramos una clase abstracta para declarar los metodos necesarios para obtener datos de Amazon
# - getProductPrize() -> Obtiene el precio de un producto
# - getProductStock() -> Obtiene el stock de un producto

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

    # Obtiene el titulo y el precio de un producto que NO TIENE STOCK
    async def getProductStock(self, s, url):
        title = None
        stock = None

        try:
            response = await s.get(url)  # Se pasa la URL del producto a rastrear
            await response.html.arender(wait=2)  # Espera a que renderice la pagina

            title = response.html.xpath('//*[@id="productTitle"]', first=True).text  # Obtiene el titulo
            stock = response.html.xpath('//*[@id="availability"]/span', first=True).text  # Obtiene el stock
        except Exception as e:
            print(e)

        await s.close()
        return title, stock

    # Obtiene el titulo y el precio de un producto que tiene stock
    async def getProductPrize(self, s, url):
        title = None
        prize = None

        try:
            response = await s.get(url)  # Se pasa la URL del producto a rastrear
            await response.html.arender(wait=2)  # Espera a que renderice la pagina

            title = response.html.xpath('//*[@id="productTitle"]', first=True).text  # Obtiene el titulo
            prize = response.html.find('span.a-offscreen', first=True).text  # Obtiene el precio del producto

        except Exception as e:
            print(e)

        await s.close()
        return title, prize

    # Metodo main que gestiona las peticiones de forma asincrona mediante tareas. Dos parametros:
    # url: La url a la que se realiza la peticion
    # action : Se indica la accion a realizar para llamar al metodo necesario
    async def main(self, url, action):
        global task
        s = AsyncHTMLSession()
        if action == 'stock':
            task = self.getProductStock(s, url)
        if action == 'precio':
            task = self.getProductPrize(s, url)
        await s.close()
        return await task
