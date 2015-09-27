# coding:utf8
import time
import threading
from spiderx_logger import logger
import random
import urllib2
from crawler_models import Response, Url


class Crawler(threading.Thread):
    """
    Crawler(url, gzip=False, snapshot=False).crawling(), Return response
    """

    def __init__(self, m_url, gzip=False, snapshot=False, c_time=0):
        threading.Thread.__init__(self)
        self.agents = [('Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36'
                        ' (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36'),
                       ('Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36'
                        ' (KHTML, like Gecko) Chrome/40.0.2214.94 Safari/537.36'),
                       ('Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.3; WOW64;'
                        ' Trident/7.0; .NET4.0E; .NET4.0C; InfoPath.3)'),
                       ('Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36'
                        ' (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36')]

        self.url = m_url
        self.gzip = gzip
        self.snapshot = snapshot
        self.header = {'User-Agents': self.agents[random.randint(0, len(self.agents) - 1)], 'Referer': self.url}
        self.logger = logger()
        self.c_time = c_time

        self.simple_open_url = lambda: urllib2.urlopen(urllib2.Request(self.url, headers=self.header)).read()

    def open_url(self):
        if self.c_time > 10:
            return {}
        req = urllib2.Request(self.url, headers=self.header)
        try:
            response = urllib2.urlopen(req, timeout=10)
        except urllib2.HTTPError, e:
            self.logger.error(
                'Url open error, ' + str(e) + 'return ' + str({'response': '', 'code': e.code, 'url': self.url}))
            return {'response': '', 'code': e.code, 'url': self.url}
        except Exception, ee:
            self.logger.error('Unknow Error: ' + str(ee.args) + ', re-crawled after 3 seconds')
            time.sleep(3)
            return Crawler(self.url, c_time=self.c_time+1).open_url()

        res = dict({})
        res['url'] = response.geturl()
        res['code'] = response.code
        if self.snapshot and response.code == 200:
            # start the snapshot thread
            self.start()
        for key, value in response.headers.dict.items():
            if key == 'content-encoding' or key == 'content-type':
                res[key] = value
        try:
            res['response'] = response.read()
        except Exception, ee:
            self.logger.error('Unknow Error: ' + str(ee.args) + ', re-crawled after 3 seconds')
            time.sleep(3)
            return Crawler(self.url, c_time=self.c_time+1).open_url()
        return res

    def crawling(self):
        """
        main crawling

        if code is 200, return (data, url[, content-type])
        if code is not 200, return ('', url, code)
        """
        time.sleep(random.random() * 3)
        response = self.open_url()
        if not len(response):
            self.logger.error('None response!')
            return Response()
        # response's keys is url, code[, content-encoding] [, content-type], html
        response_code = response.get('code')
        if response_code != 200:
            self.logger.warning('response code: ' + str(response_code))
            return Response(url=response.get('url', ''))
        content_encoding = response.get('content-encoding', '')
        self.gzip = True if 'gzip' in content_encoding else False
        content_type = response.get('content-type', '')

        if self.gzip:
            import gzip

            t_gzip_path = 'temp%s.txt.gz' % time.time()
            self._save_html(response.get('response'), t_gzip_path)

            try:
                gziper = gzip.open(t_gzip_path, 'rb')
                res = gziper.read()
                gziper.close()
                self.logger.info('Return gzip response, url:' + response.get('url'))
                return Response(response=res, c_type=content_type, url=response.get('url'))
            except Exception, e:
                self.logger.error('gzip error ' + str(e))
                raise e
            finally:
                import os

                if os.path.exists(t_gzip_path) and os.path.isfile(t_gzip_path):
                    os.remove(t_gzip_path)
        else:
            self.logger.info('Return response, url:' + response.get('url'))
            return Response(response=response.get('response'), url=response.get('url'), c_type=content_type)

    def _save_html(self, html, path):
        """
        save the param html to local

        if response is gzip encoding, save as binary
        else save as text
        """
        if len(path):
            f = open(path, 'w') if not self.gzip else open(path, 'wb')
            f.write(html)
            f.close()
        else:
            self.logger.error('save html no path')

    def run(self):
        """
        snapshot sub-thread
        this method should call the IECapt in the windows platform
        !!!!It's not stable!!!!Sometimes it will crash!
        """
        import os
        import sys

        if 'win' in sys.platform:
            # snapshot save to 'cwd'\\snapshots\\'web'\\snapshot_'savetime'.jpg
            # 'web' come from the url
            import commvals
            snapshot_path = commvals.SNAPSHOTS_DIR + '%s\\snapshot_%s.jpg' % (self.url.split('.')[1].upper(),
                                                                              str(int(time.time())))
            cmd = 'IECapt --url=%s --out=%s' % (self.url, snapshot_path)
            try:
                os.popen(cmd)
                self.logger.info('get snapshot finish ---->' + snapshot_path)
            except Exception, e:
                self.logger.error('Get snapshot error: ' + str(e))
                raise e
            from spider.models import Sites, Snapshots
            site_id = Sites.objects.filter(status='A').filter(url=self.url).all()[0].id
            try:
                snapshot = Snapshots.objects.get(status=u'A', site_id=site_id)
                snapshot.status = u'D'
                snapshot.save()
            except Snapshots.DoesNotExist, e:
                self.logger.warning('not data')
            snapshot = Snapshots(path=snapshot_path,
                                 site_id=site_id)
            snapshot.save()
        else:
            self.logger.error('snapshot not support this platform --> ' + sys.platform)


"""
Test
"""
if __name__ == '__main__':
    import django
    django.setup()
    url = ['http://www.youku.com',
           'http://www.bilibili.com/index/recommend.json',
           'http://www.chiark.greenend.org.uk/~sgtatham/putty/downloads.html',
           'http://www.bilibili.com',
           'http://www.bilibili.com/index/ranking.json',
           'http://v.youku.com/v_show/id_XODMxNzI4MjQ4.html',
           'http://tv.sohu.com/20150307/n409457695.shtml?ref=360',
           'http://tv.sohu.com/20140703/n401699263.shtml?ref=360']
    # res = Crawler(url[1]).crawling()  # html
    # import json
    # d = json.loads(res[0])
    # print d[u'list'][0][u'description']
    # print Crawler(url[1]).crawling() #json-str, gzip
    res = Crawler(url[6]).crawling()
    out = res.response
    f = open('out.txt', 'w')
    f.write(out)
    f.close()