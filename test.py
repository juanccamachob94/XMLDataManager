# import requests

url = 'https://www.adn40.mx/noticia/seguridad/notas/2011-03-10-15-05/lo-agarran-en-tamaulipas'
# r = requests.get(url)
# print(r.text)

import ssl
import urllib.request
import tempfile

from bs4 import BeautifulSoup

ssl._create_default_https_context = ssl._create_unverified_context

temporary_file_wrapper = tempfile.NamedTemporaryFile(suffix='.html')
urllib.request.urlretrieve(url, temporary_file_wrapper.name)

temporary_html_route = temporary_file_wrapper.name

with open(temporary_html_route) as fp:
    soup = BeautifulSoup(fp, "html.parser")
    print(soup.find_all('div', class_='CreativeWorkPage-section')[0].get_text())

temporary_file_wrapper.close()



