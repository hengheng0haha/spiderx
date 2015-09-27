# coding:utf8
import time as sleep_time
import spider.status as status
import os
import spider.commvals as commvals
from spider.config_loader import ConfigLoader
import threading
from spider.api import save_ranking_list, config, save_popular, load_next_start_time, save_table_for_charts
from spider.spiderx_logger import logger
sta = status.Status()
interval_time = 0, 0, 0, 0
thread_num = 0


def _work():
    from spider.url_queue import UrlQueue
    from spider.job import Job
    from spider.crawler_models import Url
    loader = ConfigLoader(commvals.CRAWLER_CONFIG_XML)
    urls = UrlQueue()
    for i in range(len(loader.sites)):
        site = loader.get_site(i)
        host = site.get('host_url')
        value = site.get('value')
        logger().info('%s Start!' % value)
        url = Url(url=host, url_tip=value, url_type='host')
        urls.put(url)
        threads = [Job(i) for i in range(thread_num)]

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        for thread in threads:
            del thread
        del threads
        logger().info('%s Finish!' % value)

    from spider.models import Videos
    Videos.objects.filter(playcount=0).delete()
    Videos.objects.filter(status='B').delete()


def _run_task(func, day=0, hour=0, minute=0, second=0):
    _delay_time = ((day * 24 + hour) * 60 + minute) * 60 + second
    _MIN = 30 * 60
    if _delay_time < _MIN:
        raise Exception('Task\'s delay time must more than 30 minutes!')

    next_start_time = map(int, load_next_start_time())
    from datetime import datetime, date, time
    t = datetime.combine(date(next_start_time[0], next_start_time[1], next_start_time[2]),
                         time(next_start_time[3], next_start_time[4], next_start_time[5]))
    now = datetime.fromtimestamp(sleep_time.time())
    if now < t:
        logger().info("Next start time: %s" % t.strftime('%Y-%m-%d %H:%M:%S'))
        delta = (t - now).total_seconds()
        while delta > 0:
            sleep_time.sleep(2)
            delta -= 2

    while sta.ncompare(status.STATUS_STOPPED):
        temp_time = _delay_time
        iter_now = datetime.now()
        iter_now_time = iter_now.strftime('%Y-%m-%d %H:%M:%S')
        save_start_time(iter_now_time)
        logger().info("start work: %s" % iter_now_time)
        if sta.ncompare(status.STATUS_RUNNING):
            sta.status(status.STATUS_RUNNING)
        func()
        logger().info("saving ranking list...")
        save_ranking_list()
        logger().info("saving popular...")
        save_popular()
        logger().info("saving table data for charts...")
        save_table_for_charts()
        logger().info("task done.")
        logger().info("Next start time: %s" % load_next_start_time(str))
        if sta.ncompare(status.STATUS_STOPPED):
            sta.status(status.STATUS_WAITING)
        while temp_time > 0 and sta.compare(status.STATUS_WAITING):
            sleep_time.sleep(5)
            temp_time -= 5


def init():
    import os
    import spider.commvals as commvals
    from spider.config_loader import ConfigLoader
    from spider.models import Sites
    conf = ConfigLoader(commvals.CRAWLER_CONFIG_XML)
    for site in conf.sites:
        path = commvals.SNAPSHOTS_DIR + conf.get_site(site).get('host_url').split('.')[1].upper()
        m_site = conf.get_site(site)
        if not os.path.exists(path):
            os.makedirs(path)
        if not len(Sites.objects.filter(status='A', name=site).all()):
            db_site = Sites()
            db_site.name = m_site.get('value')
            db_site.ch_name = m_site.get('ch_name')
            db_site.url = m_site.get('host_url')
            db_site.save()

    global interval_time, thread_num
    interval_time = map(int, config('interval_time'))
    thread_num = int(config('thread_num'))


def server_stop():
    sta.status(status.STATUS_STOPPED)
    from spider.url_queue import UrlQueue
    temp = UrlQueue()
    for i in range(temp.size()):
        try:
            u = temp.get()
        except Exception, e:
            if temp.size() == 0:
                break
            else:
                pass
    from spider.models import Videos
    Videos.objects.filter(playcount=0).delete()
    Videos.objects.filter(status='B').delete()


def server_start():
    sta.status(status.STATUS_RUNNING)
    if sta.ncompare(status.STATUS_STOPPED):
        init()
        # sta.status(status.STATUS_RUNNING)
        _run_task(_work, day=interval_time[0], hour=interval_time[1], minute=interval_time[2], second=interval_time[3])


def server_restart():
    server_stop()
    while sta.compare(status.STATUS_RUNNING):
        sleep_time.sleep(0.5)
    server_start()


def save_start_time(start_time):
    import re
    file_name = commvals.RESOURCES_DIR + 'config.conf'
    f = open(file_name, 'r')
    conf = f.read()
    f.close()
    times = 'start_time='+str(start_time)
    conf = re.sub(r'start_time=\d+-\d+-\d+ \d+:\d+:\d+', times, conf)
    f = open(file_name, 'w')
    f.write(conf)
    f.close()


class WebServerThread(threading.Thread):
    def __init__(self):
        super(WebServerThread, self).__init__()

    def run(self):
        import subprocess
        p = subprocess.Popen('python manage.py runserver', stdout=subprocess.PIPE, shell=True)
        print p.stdout.readlines()

if __name__ == '__main__':
    import sys
    sys.path.append('C:/Users/Baxter/Desktop/spiderx')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spiderx.settings")
    import django
    django.setup()

    if config('open_dev_web_server') == 'true':
        WebServerThread().start()
    server_start()
