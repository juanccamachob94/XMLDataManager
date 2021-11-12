"""
    Sources: https://stackoverflow.com/questions/24124643/parse-xml-from-url-into-python-object
"""
import ssl # to connect with external url resources
import requests
import xmltodict

# context to allow access to external file resources (https://...)
ssl._create_default_https_context = ssl._create_unverified_context

xml_url = 'https://www.adn40.mx/sitemap.xml'

xml_content_ordered_dict = xmltodict.parse(requests.get(xml_url).content)
print(xml_content_ordered_dict['sitemapindex'])
