# Este srcipt obtiene proxies con protocolo HTTP de la página https://free-proxy-list.net/ y los almacena en un CSV
from bs4 import BeautifulSoup  # Imports scraping module
import requests
import concurrent.futures
import csv

def getProxies():
    proxieslist = []
    with open("Free_Proxy_List.csv", "r") as csv_file:
        next(csv_file)
        reader = csv.reader(csv_file)
        for i in reader:
            proxieslist.append(i[0]+':'+i[7])


    with open("proxieslist.csv", "w") as csv_file:
        for row in proxieslist:
            csv_file.write("".join(row) + "\n")

    # Gets proxieslist
    with open("proxieslist.csv", "r") as csv_file:
        proxylist = csv_file.read().splitlines()

    # Comprueba que los proxies obtenidos funcionan
    print('=== Checking Proxies ===')
    workingProxies = []
    def checkProxy(proxy):
        r = ""
        try:
            r = requests.get('https://httpbin.org/ip', proxies={'http': proxy, 'https': proxy}, timeout=3)
            print(r.json(), ' - working')
            workingProxies.append(proxy)
        except:
            print('Proxy not working')
        return proxy

    # Comprobamos concurrentemente todos los proxies obtenidos
    with concurrent.futures.ThreadPoolExecutor() as executor:
        proxies = executor.map(checkProxy, proxylist)
        print(proxies)

    # Saves working proxies in file
    with open("workingproxies.csv", "w") as csv_file:
        for row in workingProxies:
            csv_file.write("".join(row) + "\n")

# === Fin getProxies() ===

def getWorkingProxies():
    # Devuelve la lista con los proxies que funcionan
    with open("workingproxies.csv", "r") as csv_file:
        workingproxies = csv_file.read().splitlines()
        return workingproxies

if __name__ == "__main__":
    getProxies()
    getWorkingProxies()