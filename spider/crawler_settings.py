# coding:utf8
__author__ = 'Baxter'
from config_loader import ConfigLoader
import commvals
from api import deal_url_format


class Settings():
    def __init__(self, tip):
        loader = ConfigLoader(commvals.CRAWLER_CONFIG_XML)

        SITES = loader.sites

        SITE = SITES[SITES.index(tip.upper())]

        host_element = loader.get_element(SITE, 'host').get('element', [{}])[0]

        video_element = loader.get_element(SITE, 'video').get('element', [{}])[0]

        self.site = SITE

        self.able = False if loader.get_site(SITE).get('able', 'true') == 'false' else True

        self.host_url = loader.get_site(SITE).get('host_url')

        self.url_format = deal_url_format(loader.get_site(SITE).get('url_format'))

        self.snapshot = False if loader.get_site(SITE).get('snapshot', 'true') == 'false' else True

        self.video_url_end = loader.get_site(SITE).get('video_url_end', '')

        self.host = {
            'onlyurl': True if host_element.get('onlyurl', 'false') == 'true' else False,
            'request': host_element.get('request', ''),
            'param': host_element.get('param', ''),
            'children': tuple([child.tag for child in loader.get_children(SITE, 'host')]),
            'filter': loader.get_element(SITE, 'filter').get('element')
        }

        self.video = {
            'request': video_element.get('request', ''),
            'param': video_element.get('param', ''),
            'isre': True if video_element.get('isre', 'false') == 'true' else False,
            'children': tuple([child.tag for child in loader.get_children(SITE, 'video')]),
            'null': video_element.get('request', '') == '' and video_element.get('param', '') == ''
        }

        self.url = loader.get_element(SITE, 'url').get('element', [])

        self.title = loader.get_element(SITE, 'title').get('element', [])

        self.thumbnail = loader.get_element(SITE, 'thumbnail').get('element', [])

        self.playcount = loader.get_element(SITE, 'playcount').get('element', [])

        self.community = loader.get_element(SITE, 'community').get('element', [])

        self.upcount = loader.get_element(SITE, 'upcount').get('element', [])

        self.downcount = loader.get_element(SITE, 'downcount').get('element', [])

        self.favorite = loader.get_element(SITE, 'favorite').get('element', [])

        self.host_children = []

        self.video_children = []

        self.init_children()

    def init_children(self):
        host_chi = self.host.get('children')
        video_chi = self.video.get('children')
        items = {
            'url': self.url,
            'thumbnail': self.thumbnail,
            'title': self.title,
            'playcount': self.playcount,
            'community': self.community,
            'upcount': self.upcount,
            'downcount': self.downcount,
            'favorite': self.favorite
        }
        for key, value in items.items():
            if key in host_chi:
                self.host_children.append((key, value))
            elif key in video_chi:
                self.video_children.append((key, value))