"""
    Sources: https://stackoverflow.com/questions/24124643/parse-xml-from-url-into-python-object
"""
import ssl # to connect with external url resources
import requests
import xmltodict

# context to allow access to external file resources (https://...)
ssl._create_default_https_context = ssl._create_unverified_context

class XMLReader:
    @classmethod
    def perform(cls, url):
        # return a XML Content Oredered Dict object <class 'collections.OrderedDict'>
        return xmltodict.parse(requests.get(url).content)

class SiteMapIndexReader:
    ROOT_CONTAINER_NAME = 'sitemapindex'

    @classmethod
    def complete_list(cls, xml_url):
        """
            return the <sitemap> collection; each item is a OrderedDict instance
            with the keys locm and lastmod of xml file.
        """
        return list(XMLReader.perform(xml_url).get(cls.ROOT_CONTAINER_NAME, []).get('sitemap', []))


    @classmethod
    def list_by_lastmod(cls, xml_url, lastmod):
        """
            lastmod represents a date when the resource was modified
            lastmod is a <str> that allows the next formats:
            aaaa-mm- => 2021-09-
            aaaa-mm-dd => 2021-09-03
            aaaa-mm-ddThh:mm-ss:mmmm => 2021-09-03T10:20-05:00
        """
        return list(
            filter(
                lambda sitemap: cls.__is_valid_sitemap(sitemap, lastmod),
                cls.complete_list(xml_url)
            )
        )


    @classmethod
    def first_by_lastmod(cls, xml_url, lastmod):
        # first in the list based on the xml file location
        lastmod_list = cls.list_by_lastmod(xml_url, lastmod)
        return lastmod_list[0] if len(lastmod_list) else None


    @classmethod
    def last_by_lastmod(cls, xml_url, lastmod):
        # last in the list based on the xml file locations
        lastmod_list = cls.list_by_lastmod(xml_url, lastmod)
        return lastmod_list[len(lastmod_list) - 1] if len(lastmod_list) else None


    @classmethod
    def __is_valid_sitemap(cls, sitemap, lastmod):
        sitemap.get('lastmod', '').startswith(lastmod) \
            and sitemap.get('loc') != None

class ADN40SiteMapIndexReader:
    XML_URL = 'https://www.adn40.mx/sitemap.xml'

    @classmethod
    def perform(cls, lastmod, location_type='first'):
        # returns an array of OrderedDict instances
        if location_type == 'first':
            sitemaps = [SiteMapIndexReader.first_by_lastmod(cls.XML_URL, lastmod)]
        elif location_type == 'last':
            sitemaps = [SiteMapIndexReader.last_by_lastmod(cls.XML_URL, lastmod)]
        else:
            sitemaps = SiteMapIndexReader.list_by_lastmod(cls.XML_URL, lastmod)
        return list(filter(None, sitemaps))



for sitemap in ADN40SiteMapIndexReader.perform('2021-10'):
    print(sitemap)
