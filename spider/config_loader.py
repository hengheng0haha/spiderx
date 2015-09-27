# coding:utf8
from spiderx_logger import logger
from lxml import etree
import commvals
ELEMENTS_WORDS = ['url', 'thumbnail', 'filter', 'playcount', 'title',
                  'community', 'upcount', 'downcount', 'favorite',
                  'host', 'video']


class ConfigLoader(object):
    """docstring for ConfigLoader"""

    def __init__(self, path=''):
        super(ConfigLoader, self).__init__()
        self.logger = logger()
        self.path = path if len(path) else commvals.CRAWLER_CONFIG_XML
        self.doc = etree.parse(self.path)
        self.site = self.doc.xpath(u'//site')
        self.sites = [site.attrib.get('value', '') for site in self.site if site.attrib.get('able', 'true') == 'true']

    def get_element(self, site, location):
        """
        load:
            elements(element),
            parent(parent),
            grandparent(site)
        """
        res = {}
        if not location or not site:
            return res
        if location not in ELEMENTS_WORDS:
            self.logger.error("unknow loaction " + location)
            return res

        index = self.sites.index(site.upper())
        site = self.site[index]

        if site.attrib.get('able', 'True') == 'false':
            return res

        tags = [child.tag for child in site]

        if location in tags:
            res['element'] = [site.find(location).attrib]
            res['parent'] = res['site'] = site.attrib
            return res

        for tag in tags:
            elements = site.find(tag).findall(location)
            if len(elements):
                res['element'] = [element.attrib for element in elements]
                res['parent'] = element.getparent().attrib
                break

        if len(res):
            res['site'] = site.attrib
        return res

    def get_site(self, key):
        if isinstance(key, str):
            if len(key) and key.upper() in self.sites:
                key = self.sites.index(key.upper())
            else:
                return {}
        elif isinstance(key, int):
            if key >= len(self.sites) or key < 0:
                return {}
        return self.site[key].attrib

    def get_children(self, site, element):
        if site.upper() not in self.sites:
            return []
        if element not in ['host', 'video']:
            return []
        m_site = self.site[self.sites.index(site.upper())]
        parent = m_site.find(element)
        children = []
        if parent is not None:
            children = parent.getchildren()
        result = []
        for child in children:
            if child.tag != 'filter':
                result.append(child)
        return result


def get_params(t):
    """
    get params from param file
    """
    if not len(t):
        return []
    if t.startswith('file:'):
        return open(commvals.RESOURCES_DIR + t[t.index(':') + 1:], 'r').read().split('\n')
    return []


def get_from_html(html, location):
    import re
    # html = re.sub(r'charset=(\w*)', 'charset=UTF-8', html)
    doc = etree.HTML(html)
    return doc.xpath(location)


if __name__ == '__main__':
    import commvals
    from crawler import Crawler
    loader = ConfigLoader(commvals.CRAWLER_CONFIG_XML)
    l_urls = ['http://www.youku.com', 'http://www.acfun.tv']

    # print loader.get_element('YOUKU', 'thumbnail')
    # print loader.get_site(0)
    # res = loader.get_element('youku', 'url')
    # print res
    # print get_params('file:youku_community')
    # html = Crawler(l_urls[0]).crawling()[0]
    # urls = get_from_html(html, loader.get_element('youku', 'url').get('element')[0].get('location'))
    # thumbs = get_from_html(html, loader.get_element('acfun', 'thumbnail').get('element')[0].get('location'))
    # print dir(urls[0])
    # print get_params('file:bili_all')
    # children = loader.get_children('sohutv', 'host')
    # for child in children:
    #     print child.tag
    print loader.get_element('bilibili', 'video').get('element')