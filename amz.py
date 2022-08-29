from abc import ABC, abstractmethod  # Imports ABC module
from requests_html import *
import asyncio



# Declaramos una clase abstracta para declarar los metodos necesarios para obtener datos de Amazon
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

        response = await s.get(url)  # Se pasa la URL del producto a rastrear
        await response.html.arender(sleep=1)  # Espera a que renderice la pagina

        try:
            title = response.html.find('span#productTitle')[0].text
            stock = response.html.find('span.a-size-medium, a-color-success', first=True).text
            if stock == '':
                stock = response.html.find('span.a-size-medium, a-color-state', first=True).text
            else:
                pass
        except:
            stock = ''  # Devuelve vacío cuando el producto no muestra información de stock
            title = ''
        await s.close()
        return title, stock

    # Obtiene el titulo y el precio de un producto que tiene stock
    async def getProductPrize(self, s, url):

        response = await s.get(url)  # Se pasa la URL del producto a rastrear
        await response.html.arender(sleep=1)  # Espera a que renderice la pagina

        try:
            title = response.html.find('span#productTitle')[0].text
            prize = response.html.find('span.a-offscreen')[0].text
            # if prize == '':
            #     prize = response.html.find('span.a-size-medium, a-color-price, header-price, a-text-normal')[0].text
            # else:
            #     pass
        except Exception as e:
            print(e)
            title = ''
            prize = ''
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

# if __name__ == "__main__":
#     amz = AmzScraper()
#     s = AsyncHTMLSession()
#     precio = await amz.getProductPrize(s, 'https://www.amazon.es/GoPro-Kit-HERO8-Black-repuesto/dp/B08981WMRP/ref=sr_1_146?__mk_es_ES=%C3%85M%C3%85%C5%BD%C3%95%C3%91&keywords=GoPro&qid=1661428211&s=electronics&sr=1-146&th=1')
#     print(precio)