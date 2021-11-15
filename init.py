"""
    Sources: https://stackoverflow.com/questions/24124643/parse-xml-from-url-into-python-object
"""
import ssl # to connect with external url resources
import requests
import tempfile
import urllib.request
import xmltodict
from bs4 import BeautifulSoup

# context to allow access to external file resources (https://...)
ssl._create_default_https_context = ssl._create_unverified_context

class XMLReader:
    @classmethod
    def perform(cls, url):
        # return a XML Content Oredered Dict object <class 'collections.OrderedDict'>
        return xmltodict.parse(requests.get(url).content)


class DefaultReader:
    ROOT_CONTAINER_NAME = None
    ITEM_CONTAINER_NAME = None

    @classmethod
    def complete_list(cls, xml_url):
        """
            return the <sitemap> collection; each item is a OrderedDict instance
            with the keys locm and lastmod of xml file.
        """
        content = XMLReader.perform(xml_url) \
            .get(cls.ROOT_CONTAINER_NAME, {}).get(cls.ITEM_CONTAINER_NAME, [])
        if isinstance(content, list):
            return content
        return [content]


class SiteMapIndexReader(DefaultReader):
    ROOT_CONTAINER_NAME = 'sitemapindex'
    ITEM_CONTAINER_NAME = 'sitemap'

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
        sitemap_lastmod = sitemap.get('lastmod')
        sitemap_lastmod and sitemap_lastmod.startswith(lastmod) \
            and sitemap.get('loc') != None
        return True


class SiteMapReader(DefaultReader):
    ROOT_CONTAINER_NAME = 'urlset'
    ITEM_CONTAINER_NAME = 'url'

    @classmethod
    def news_list(cls, xml_url):
        return list(filter(lambda item: cls.__is_a(item, 'news'), cls.complete_list(xml_url)))


    @classmethod
    def video_list(cls, xml_url):
        return list(filter(lambda item: cls.__is_a(item, 'video'), cls.complete_list(xml_url)))


    @classmethod
    def __is_a(cls, item, expected_type):
        return item.get(''.join([expected_type, ':', expected_type]), False)


class AccountSiteMapIndexReader:
    @classmethod
    def perform(cls, xml_url, lastmod, location_type='first'):
        # returns an array of OrderedDict instances
        sitemaps = []
        if location_type == 'first':
            sitemaps = [SiteMapIndexReader.first_by_lastmod(xml_url, lastmod)]
        elif location_type == 'last':
            sitemaps = [SiteMapIndexReader.last_by_lastmod(xml_url, lastmod)]
        else:
            sitemaps = SiteMapIndexReader.list_by_lastmod(xml_url, lastmod)
        return list(filter(None, sitemaps))

class AccountSiteMapReader:
    @classmethod
    def perform(cls, xml_url, expected_type='news'):
        if expected_type == 'news':
            return SiteMapReader.news_list(xml_url)
        elif expected_type == 'videos':
            return SiteMapReader.video_list(xml_url)
        else:
            return SiteMapReader.complete_list(xml_url)


class NewsSitemapPageContentDictGenerator:
    @classmethod
    def perform(cls, url):
        temporary_file_wrapper = tempfile.NamedTemporaryFile(suffix='.html')
        urllib.request.urlretrieve(url, temporary_file_wrapper.name)
        with open(temporary_file_wrapper.name) as fp:
            page_main_content = BeautifulSoup(fp, "html.parser") \
                .find('article', class_='Page-mainContent')
            meta_tag_element = page_main_content.find('div', class_='CreativeWorkPage-metas')
            sub_headline = page_main_content.find('div', class_='CreativeWorkPage-subHeadline')
            article_body = page_main_content.find('div', class_='ArticlePage-articleBody')
            news_data = {
                'author':
                    meta_tag_element.find('div', class_='CreativeWorkPage-authorName').get_text(),
                'category':
                    meta_tag_element.find('div', class_='CreativeWorkPage-section').get_text(),
                'content': cls.__build_content(sub_headline, article_body),
                'html_content': cls.__build_html_content(sub_headline, article_body)
            }
        temporary_file_wrapper.close()
        return news_data


    @classmethod
    def __build_content(cls, sub_headline, article_body):
        return ''.join([sub_headline.get_text(), ' ', article_body.get_text()])


    @classmethod
    def __build_html_content(cls, sub_headline, article_body):
        return ''.join([str(sub_headline), str(article_body)])

class NewsSitemapContentDictGenerator:
    @classmethod
    def perform(cls, sitemap_content_item):
        dict_news_sitemap_content = {
            'title': sitemap_content_item.get('news:news', {}).get('news:title', None)
        }
        dict_news_sitemap_content.update(
            NewsSitemapPageContentDictGenerator.perform(sitemap_content_item.get('loc'))
        )
        return dict_news_sitemap_content

class SitemapContentProcessor:
    @classmethod
    def perform(cls, sitemap_content_item, expected_type='news'):
        if expected_type == 'news':
            return NewsSitemapContentDictGenerator.perform(sitemap_content_item)
        return None

for sitemap in AccountSiteMapIndexReader.perform('https://www.adn40.mx/sitemap.xml', '2021-10'):
    for sitemap_content_item in AccountSiteMapReader.perform(sitemap['loc']):
        print(SitemapContentProcessor.perform(sitemap_content_item))
