# coding:utf8
import threading
from url_queue import UrlQueue
from crawler import Crawler
from config_loader import get_from_html
import commvals
from spiderx_logger import logger
from crawler_settings import Settings
from spider.models import Videos, Sites
import json
from api import build_request, find_dict, delete_same, get_from_dict
from crawler_models import Url, Response
import status


class Job(threading.Thread):
    """docstring for Job"""
    urls = UrlQueue()
    logger = logger()
    settings = ''
    stat = status.Status()

    def __init__(self, i):
        super(Job, self).__init__()
        self.thread_num = i

    def run(self):
        import time
        counter = 0
        while True:
            if self.stat.ncompare(status.STATUS_RUNNING):
                break
            url = self.urls.get()
            if not url:
                if counter >= 30:
                    break
                counter += 1
                if counter % 10 == 0:
                    self.logger.info('Job(%d) waiting for url...(%d)' % (self.thread_num, counter))
                time.sleep(1)
                continue
            self.settings = Settings(url.url_tip)
            response = Crawler(m_url=url.url, snapshot=self.settings.snapshot and url.url_type == 'host').crawling()
            if not len(response.response):
                self.logger.error('None response')
                continue
            if url.url_type == 'host':
                host_children = self.settings.host.get('children')
                import re

                response.response = re.sub(r'charset=(\w*)', 'charset=UTF-8', response.response)
                if self.settings.host.get('onlyurl'):
                    self.host_only_url(response=response, children=host_children)
                else:
                    self.host_not_only_url(children=host_children)
            elif url.url_type == 'video':
                # do video
                video_children = self.settings.video.get('children')
                if self.settings.video.get('null'):
                    self.video_null(response=response, children=video_children, url=url)
                else:
                    self.video_not_null(response=response, children=video_children, url=url)

    def host_only_url(self, response=None, children=None):
        if response and children:
            html = response.response
            infos = {}
            for key, child in self.settings.host_children:
                infos[key] = get_from_html(html, child[0].get('location'))
            n = []
            for item in infos.get('url'):
                get = self.settings.url[0].get('get')
                identity = self.settings.url[0].get('id')
                # res_url = item.attrib.get(get)
                res_url = get_from_dict(item.attrib, get.split('|'))
                if len(self.settings.url_format):
                    flag = False
                    for f in self.settings.url_format:
                        if res_url.startswith(f):
                            flag = True
                            break
                if not flag:
                    continue

                if not res_url.startswith('http://'):
                    res_url = self.settings.host_url + res_url

                filters = self.settings.host.get('filter')
                if filters is not None:
                    flag = True
                    for fil in filters:
                        f_type = fil.get('type', '')
                        f_value = fil.get('value')
                        if len(f_type) and f_value not in res_url:
                            flag = False
                            break
                        elif not len(f_type) and f_value in res_url:
                            flag = False
                            break
                    if not flag:
                        continue

                d = {}
                d.update({'url': res_url, 'id': get_from_dict(item.attrib, identity.split('|'))})
                n.append(d)
            result = []
            for item in infos.get('thumbnail'):
                get = self.settings.thumbnail[0].get('get')
                identity = self.settings.thumbnail[0].get('id')
                if '_' + get in item.attrib.keys():
                    get = '_' + get
                # res_thumb = item.attrib.get(get)
                res_thumb = get_from_dict(item.attrib, get.split('|'))
                if identity.startswith('parent:'):
                    id_thumb = item.getparent().attrib.get(identity.split('parent:')[1])
                else:
                    # id_thumb = item.attrib.get(identity)
                    id_thumb = get_from_dict(item.attrib, identity.split('|'))
                for i in n:
                    if i.get('id') == id_thumb:
                        i.update({'thumbnail': res_thumb})
                        result.append(i)
                        break
            result = delete_same(result)
            for item in result:
                site = Sites.objects.get(name=self.settings.site)
                video = Videos.objects.create(url=item.get('url')+self.settings.video_url_end, thumbnail=item.get('thumbnail'), site_id=site.id)
                next_url = Url(url=video.url, url_type='video', url_tip=self.settings.site, id_indb=video.id)
                self.urls.put(next_url, block=True)

    def host_not_only_url(self, children=None):
        if not children:
            return None
        requests = build_request(self.settings.host.get('request'), self.settings.host.get('param'))
        all_data = []
        for request in requests:
            response = Crawler(request).crawling()
            m_json = json.loads(response.response)
            items = find_dict(m_json, u'aid')
            for item in items:
                save = dict()
                for key, value in self.settings.host_children:
                    v = item.get(value[0].get('key'))
                    if key == 'url' and not str(v).startswith('http://'):
                        v = self.settings.url_format[0] + str(v)
                    if key == 'title':
                        v = v.encode('utf8')
                    if key in ['playcount', 'favorite', 'community', 'upcount', 'downcount'] and not isinstance(v, int):
                        try:
                            v = int(v)
                        except Exception, e:
                            self.logger.error('Unknow value ' + v + ' ' + key)
                            v = 0
                    save[key] = v
                    site_id = Sites.objects.get(name=self.settings.site, status=u'A').id
                    save.update({'site_id': site_id})
                all_data.append(save)
        all_data = delete_same(all_data)
        for data in all_data:
            data.update({'status': 'A'})
            video = Videos(**data)
            video.save()

    def video_null(self, response=None, children=None, url=None):
        if not response:
            return None
        result = dict()
        for key, value in self.settings.video_children:
            if len(value):
                way = value[0].get('way')
                if way == 'html':
                    location = value[0].get('location')
                    get = get_from_html(response.response, location)
                    if not len(get):
                        self.logger.error('Error response, url:' + url.url)
                        self.urls.put(url)
                        return None
                    if key == 'title':
                        result[key] = get[0].text
                    else:
                        if 'get' not in value[0].keys():
                            result[key] = get[0].text
                        else:
                            pass
                elif way == 'json':
                    m_split = value[0].get('split', '')
                    json_key = value[0].get('key')
                    request = build_request(template=value[0].get('request'),
                                            param=value[0].get('param'),
                                            isre=value[0].get('isre', False),
                                            html=response.response)
                    if not len(request):
                        continue
                    json_response = Crawler(request[0]).crawling()
                    if len(m_split):
                        m_start = json_response.response.index(m_split.split(':')[0])
                        m_end = json_response.response.index(m_split.split(':')[1])
                        json_response.response = json_response.response[m_start + 1:m_end]
                    try:
                        d = json.loads(json_response.response)
                        if isinstance(d, dict):
                            res = find_dict(d, json_key)
                            if len(res):
                                result[key] = res[0].get(json_key)
                        elif isinstance(d, int):
                            result[key] = d
                    except ValueError, ve:
                        pass
        for key, value in result.items():
            if key not in ['title', 'url', 'thumbnail']:
                if not isinstance(value, int):
                    value = int(value.replace(',', ''))
                    result.update({key: value})
            result.update({'status': 'A'})
        video = Videos.objects.filter(id=url.id_indb).update(**result)

    def video_not_null(self, response=None, children=None, url=None):
        if response and children:
            video = self.settings.video
            request = build_request(template=video.get('request'),
                                    param=video.get('param'),
                                    isre=video.get('isre'),
                                    html=response.response)[0]
            resp = Crawler(request).crawling()
            json_response = json.loads(resp.response)
            result = dict()
            for key, value in self.settings.video_children:
                if len(value):
                    way = value[0].get('way')
                    if way == 'html':
                        location = value[0].get('location')
                        get = get_from_html(response.response, location)
                        if key == 'title':
                            temp = get[0].text
                            if not temp:
                                result[key] = get[0].attrib.get('title', '').encode('utf8')
                            else:
                                result[key] = temp.encode('utf8')
                        else:
                            result[key] = get[0].text.encode('utf8') if key == 'title' else get[0].text
                    elif way == 'json':
                        json_key = ''
                        if 'key' in value[0].keys():
                            json_key = value[0].get('key')
                        elif 'index' in value[0].keys():
                            json_key = int(value[0].get('index'))
                        result[key] = json_response[json_key]
            result.update({'status': 'A'})
            Videos.objects.filter(id=url.id_indb).update(**result)


if __name__ == '__main__':
    import os

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spiderx.settings")
    import time
    from crawler_models import Url
    import django

    django.setup()
    queue = UrlQueue()
    # queue.put(Url(url='http://www.youku.com', url_tip='youku', url_type='host')) # 235
    # queue.put(Url(url='http://www.acfun.tv', url_tip='acfun', url_type='host')) # 129
    # queue.put(Url(url='http://tv.sohu.com', url_tip='sohutv', url_type='host')) # 299
    # queue.put(Url(url='http://www.bilibili.com', url_tip='bilibili', url_type='host'))
    # queue.put(
    # Url(url='http://v.youku.com/v_show/id_XODk0NjM0Nzcy.html', url_tip='youku', url_type='video',
    #         id_indb=257))
    queue.put(Url(url='http://tv.sohu.com/20150306/n409440063.shtml', url_tip='sohutv', url_type='video', id_indb=7200))
    # for i in range(10):


    job = Job(0)
    # queue.put(Url(url='http://tv.sohu.com/20150221/n409106225.shtml', url_tip='sohutv', url_type='video'))

    start = time.time()
    status.Status().status(status.STATUS_RUNNING)
    job.start()
    job.join()
    status.Status().status(status.STATUS_STOPPED)
    print time.time() - start
