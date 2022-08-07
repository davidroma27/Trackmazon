# For this class we need to install the following:
# - pip install BeautifulSoup
# - pip install requests

from abc import ABC, abstractmethod  # Imports ABC module
from bs4 import BeautifulSoup  # Imports scraping module
import requests
import random
import proxygetter

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
    def getProductPrize(self):
        pass

    @abstractmethod
    def getProductStock(self):
        pass


# Implementamos la clase abstracta
class AmzScraper(Scraper):

    def __init__(self, url):
        self.proxies = proxygetter.getWorkingProxies() # Proxies para realizar las peticiones
        self.proxy = self.proxies[random.choice(tuple(self.proxies))] # Escogemos un proxy aleatorio de la lista
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 OPR/89.0.4447.71'}
        self.request = requests.get(url, self.headers, proxies={'http': self.proxy, 'https': self.proxy}, timeout=3)

    def getProductStock(self):
        soup = BeautifulSoup(self.request.text, 'html.parser')
        stock = soup.select("span.a-size-medium a-color-success")
        status = self.request.status_code
        return status

    def getProductPrize(self):
        soup = BeautifulSoup(self.request.text, 'html.parser')
        prize = soup.select("span.a-offscreen")
        return prize
