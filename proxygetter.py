# Este srcipt obtiene proxies con protocolo HTTP de la página https://free-proxy-list.net/ y los almacena en un CSV
from bs4 import BeautifulSoup  # Imports scraping module
import requests
import concurrent.futures

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 OPR/89.0.4447.71'}
r = requests.get('https://free-proxy-list.net/', headers=headers)

print('Response: ' + str(r.status_code))

soup = BeautifulSoup(r.text, 'html.parser')
table = soup.find('table', class_='table table-striped table-bordered')

# Obtiene todos los proxies con el protocolo HTTPS
print('Getting proxies...')
proxies = []
try:
    for row in table.tbody.find_all('tr'):
        ishttps = row.find('td', class_='hx').text
        tds = row.find_all("td")
        if ishttps == 'yes':
            ip = tds[0].text
            port = tds[1].text
            proxy = ip + ':' + port
            proxies.append(proxy)
    print('Proxies obtained successfully')
except:
    print('An error occurred while trying to get proxies')

# Saves proxies list in file
with open("proxieslist.csv", "w") as csv_file:
    for row in proxies:
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

# Devuelve la lista con los proxies que funcionan
def getWorkingProxies():
    with open("workingproxies.csv", "r") as csv_file:
        workingproxies = csv_file.read().splitlines()
        return workingproxies