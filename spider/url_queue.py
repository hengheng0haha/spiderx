# coding:utf8
import Queue
from spiderx_logger import logger
from singleton import singleton
from crawler_models import Url
import sys
reload(sys)
sys.setdefaultencoding('utf8')


@singleton
class UrlQueue(object):
    """docstring for Urlqueue
    """
    logger = logger()
    queue = Queue.Queue(0)

    def get(self, block=False, timeout=None):
        # if block is True and queue is empty, the thread will pause
        try:
            res = self.queue.get(block=block, timeout=timeout)
            self.logger.info('Queue(get) ----->: ' + str(res))
            return res
        except Exception, e:
            return None

    def put(self, url, block=False, timeout=None):
        if isinstance(url, Url):
            # if block is True and queue is full, the thread will pause
            self.queue.put(url, block=block, timeout=timeout)
            self.logger.info('Queue(put) <-----: ' + str(url))
        else:
            self.logger.error('error url: ' + str(url))

    def size(self):
        return self.queue.qsize()

if __name__ == '__main__':
    url1 = UrlQueue()
    url2 = UrlQueue()
    url1.put(Url(url='http://www.youku.com', url_tip='youku', url_type='host'), block=True)
    print url2.size()
    print url2.get(block=True)
    url2.put(Url(url='http://www.bilibili.com', url_tip='bilibili', url_type='host'), block=True)
    print url1.get()