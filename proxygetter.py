from bs4 import BeautifulSoup  # Imports scraping module
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 OPR/89.0.4447.71'}
r = requests.get('https://free-proxy-list.net/', headers=headers)

print('Response: ' + str(r.status_code))

soup = BeautifulSoup(r.text, 'html.parser')
table = soup.find('table', class_='table table-striped table-bordered')

print('Getting proxies...')


def getProxies():
    proxies = []
    for row in table.tbody.find_all('tr'):
        ishttps = row.find('td', class_='hx').text
        tds = row.find_all("td")
        if ishttps == 'yes':
            ip = tds[0].text
            port = tds[1].text
            proxy = ip + ':' + port
            proxies.append(proxy)

    return proxies

proxieslist = getProxies()

# Saves proxies list in file
with open("proxieslist.csv", "w") as csv_file:
    for row in proxieslist:
        csv_file.write("".join(row) + "\n")
