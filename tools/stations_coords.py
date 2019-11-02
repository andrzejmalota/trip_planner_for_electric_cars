import requests
import re
from bs4 import BeautifulSoup
import json

r = requests.get('https://www.tesla.com/findus/list/superchargers/europe')
content = r.text
sc_page_urls = re.findall('(/findus/location/supercharger/\w+)', content)
print(sc_page_urls)


# get the cooridnates (latitude, longitude) for each supercharger
sc_names = []
sc_coors = {}
for sc_page_url in sc_page_urls:
    url = 'http://www.teslamotors.com' + sc_page_url
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
    rv = requests.get(url, headers=headers)
    soup = BeautifulSoup(rv.text,"lxml")
    try:
        sc_name = soup.find_all("h1")[1].text
        sc_names.append(sc_name)
    except TypeError:
        print('No h1 found')
    try:
        directions_link = soup.find('a', {'class': 'directions-link'})['href']
        lat, lng = directions_link.split('=')[-1].split(',')
        lat, lng = float(lat), float(lng)
        sc_coors[sc_name] = {'lat': lat, 'lng': lng}
    except TypeError:
        print('No href found')

with open('stations_coords.json', 'w') as fp:
    json.dump(sc_coors, fp)