# For this class we need to install the following:
# - pip install BeautifulSoup
# - pip install requests-html

from abc import ABC, abstractmethod # Imports ABC module
from bs4 import BeautifulSoup # Imports scraping module
from requests_html import HTMLSession

# Declaramos una clase abstracta para declarar los metodos necesarios para obtener datos de Amazon
# - getData(url) -> Obtiene el ID de un producto a partir de su URL (String)
# - getProductPrize(ID) -> Obtiene el precio de un producto a partir de su ID (Float)
# - getProductStock(ID) -> Obtiene el stock de un producto a partir de su ID (Boolean)

# Declaramos la clase abstracta para un producto
class AmzProduct(ABC):
    # Todos los productos se obtendrán de una URL inicial (la de cada producto)
    @abstractmethod
    def __init__(self, url):
        self.baseurl = url

    @abstractmethod
    def getProductPrize(self):
        pass

    @abstractmethod
    def getProductStock(self):
        pass


# Implementamos la clase abstracta
class Product(AmzProduct):

    def __init__(self, url):
        super().__init__(url)
        self.session = HTMLSession()
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 OPR/89.0.4447.71'}

    # Una URL de amazon tiene la siguiente estructura (Sin parametros):
    # https://www.amazon.es/realme-Smartphone-Snapdragon-Batería-SuperDart/dp/B09S6BFSX9/
    # - https://www.amazon.es/ -> Dominio
    # - realme-Smartphone-Snapdragon-Batería-SuperDart/ -> Titulo reducido del producto (Podemos prescindir de esta parte)
    # -
    def getProductPrize(self):
        url = self.baseurl
        content = self.session.get(url)
