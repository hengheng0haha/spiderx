# coding:utf8
from config_loader import ConfigLoader, get_params
from spider.spiderx_logger import logger
import datetime
import spider.commvals as commvals
import sys
from spider.models import Videos, Sites
reload(sys)
sys.setdefaultencoding('utf-8')


def build_request(template, param, isre=False, html=''):
    from spiderx_logger import logger

    log = logger()
    res = []
    if not isre:
        count = template.count('%s')
        params = get_params(param)
        if len(params) == count:
            res = [template % tuple(params)]
        elif count == 1:
            res = [template % param for param in params]
    elif isre:
        if len(html):
            import re

            m_html = html
            params = get_params(param)
            l = []

            for p in params:
                ps = p.split(' | ')
                try:
                    for i in ps:
                        find = re.compile(i).findall(m_html)
                        if len(find):
                            l.append(find[0])
                            break
                    else:
                        log.error('None result: ' + str(l) + str(params))
                except Exception, e:
                    log.error('Error %s, %s, %s' % (e.message, params, l))
            if len(l):
                # print l, template
                res = [template % tuple(l)]

    log.info("build request result: " + str(res))
    return res


def deal_url_format(string):
    return string.split('|')


def generate_id(*args):
    import hashlib
    import time
    import random

    s = ''
    flag = 1260000000000000000L
    for arg in args:
        s += str(arg)
    infoid = int(time.time()) - flag
    infoid = (infoid << 7) | random.randint(1, 10)
    s += str(infoid)
    result = hashlib.md5(s.encode('utf-8')).hexdigest()
    return result

stack = []


def find_dict(dic, k, first=True):
    global stack
    if first and len(stack):
        stack = []
    if isinstance(dic, dict) and k in dic.keys():
        stack.append(dic)
    elif isinstance(dic, dict):
        for key, value in dic.items():
            if isinstance(value, dict):
                if k in value.keys():
                    stack.append(value)
                else:
                    find_dict(value, k, first=False)
            elif isinstance(value, list):
                for i in value:
                    find_dict(i, k, first=False)
    elif isinstance(dic, list):
        for i in dic:
            find_dict(i, k, first=False)
    return stack


def delete_same(l):
    new = []
    res = []
    if isinstance(l, list):
        for item in l:
            if item.get('url') not in new:
                new.append(item.get('url'))
                res.append(item)
            else:
                temp = res[new.index(item.get('url'))]
                res[new.index(item.get('url'))].update(item if item.get('playcount') > temp.get('playcount') else temp)
    return res


def build_chart(video_name):
    from spider.models import Videos, Sites
    result = dict()
    result.update({'title': video_name,
                   'play': [],
                   'community': [],
                   'favorite': [],
                   'up': [],
                   'down': [],
                   'xAxis': []})
    videos = Videos.objects.filter(title=video_name, status=u'A').order_by('crawling_time').all()
    site_url = Sites.objects.get(id=videos[0].site_id).url
    result.update({'source': site_url})
    for video in videos:
        result['play'].append(video.playcount)
        result['community'].append(video.community)
        result['favorite'].append(video.favorite)
        result['up'].append(video.upcount)
        result['down'].append(video.downcount)
        result['xAxis'].append(video.crawling_time)
    return result


def get_from_dict(d, ps):
    res = None
    for p in ps:
        res = d.get(p, None)
        if res:
            return res
    return res


def read_ranking_list(flag):
    import os
    file_name = commvals.RESOURCES_DIR + 'ranking_list_%s.txt' % flag
    _url = []
    _title = []
    _ifup = []
    _play = []
    if not os.path.exists(file_name):
        return [], [], [], []
    f = open(file_name, 'r')
    items = f.readlines()
    f.close()
    for item in items:
        temp = item.split('|')
        _url.append(temp[0])
        _play.append(temp[1])
        _title.append(temp[2])
        _ifup.append(temp[3].split('\n')[0])
    return _title, _url, _ifup, _play


def write_ranking_list(items, flag):
    # item: url, totle_play, title, up/down/none
    file_name = commvals.RESOURCES_DIR + 'ranking_list_%s.txt' % flag
    f = open(file_name, 'w')
    s = ''
    for item in items:
        try:
            s += '|'.join(map(str, list(item))) + '\n'
        except UnicodeEncodeError, e:
            logger().error(item)
    f.write(s)
    f.close()


def save_ranking_list():
    import operator
    videos = Videos.objects.filter(status='A').order_by('-crawling_time').all()
    flags = ['1day', '3day', '7day']
    now = datetime.datetime.now()

    for flag in flags:
        urls = dict()
        flag = int(flag[:1])
        for video in videos:
            sub_time = now - video.crawling_time
            if sub_time.days > flag - 1:
                continue
            temp = urls.get(video.url, [])
            if len(temp) == 2:
                temp[1] = video.playcount
            elif len(temp) == 1:
                temp.append(video.playcount)
            else:
                temp.append(video.playcount)
            urls.update({video.url: temp})
        for key, value in urls.items():
            urls.update({key: value[0] - value[1] if len(value) == 2 else value[0]})
        sorted_result = sorted(urls.iteritems(), key=operator.itemgetter(1), reverse=True)[:10]
        old_ranking_tup = read_ranking_list(flag)
        for new_rank, item in enumerate(sorted_result):
            title = Videos.objects.filter(status='A', url=item[0]).values('title').all()[0]
            sorted_result[new_rank] += (title.get('title'), )
            if item[0] not in old_ranking_tup[1]:
                sorted_result[new_rank] += ('up', )
            else:
                old_rank = old_ranking_tup[1].index(item[0])
                if old_rank > new_rank:
                    sorted_result[new_rank] += ('down', )
                elif old_rank < new_rank:
                    sorted_result[new_rank] += ('up', )
                else:
                    sorted_result[new_rank] += ('none', )
        write_ranking_list(sorted_result, flag)


def load_ranking_list(flag):
    ranking_list = read_ranking_list(int(flag[:1]))
    return [(ranking_list[0][i], ranking_list[1][i], ranking_list[3][i], ranking_list[2][i]) for i in range(10)]


def load_next_start_time(r_type=tuple):
    import re
    file_name = commvals.RESOURCES_DIR + 'config.conf'
    f = open(file_name, 'r')
    conf = f.read()
    p = re.compile(r'start_time=(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)')
    start_time = list(re.findall(p, conf)[0])
    p = re.compile(r'interval_time=(\d,\d,\d,\d)')
    interval_time = re.findall(p, conf)[0].split(',')
    if r_type is tuple:
        return __add_date(start_time, interval_time, tuple)
    elif r_type is str:
        return __add_date(start_time, interval_time, str)


def __add_date(start_time, interval, r_type):
    from datetime import datetime, date, time, timedelta
    import re
    start_time = map(int, start_time)
    interval = map(int, interval)
    t = datetime.combine(date(start_time[0], start_time[1], start_time[2]),
                         time(start_time[3], start_time[4], start_time[5]))
    ad = timedelta(days=interval[0], hours=interval[1], minutes=interval[2], seconds=interval[3])
    t += ad
    if r_type is tuple:
        return re.findall(re.compile(r'(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)'), t.strftime('%Y-%m-%d %H:%M:%S'))[0]
    elif r_type is str:
        return t.strftime('%Y-%m-%d %H:%M:%S')


def save_popular():
    # videos = Videos.objects.filter(status='A').order_by('-crawling_time').all()
    yestoday = datetime.date.today()-datetime.timedelta(days=1)
    videos = Videos.objects.filter(status='A').exclude(crawling_time__lte=yestoday).order_by('-crawling_time').all()
    now = datetime.datetime.now()
    url_temp = []
    pop_temp = []
    for video in videos:
        sub_time = now - video.crawling_time
        if video.url not in url_temp and sub_time.days == 0:
            url_temp.append(video.url)
            pop_temp.append({'url': video.url, 'first': video.playcount, 'times': 1})
        elif video.url in url_temp:
            t = pop_temp[url_temp.index(video.url)]
            if sub_time.days > 1:
                continue
            pop_temp[url_temp.index(video.url)].update({'url': video.url,
                                                        'last': video.playcount,
                                                        'flag': t.get('first') - video.playcount,
                                                        'times': t.get('times') + 1})
    if len(pop_temp):
        result = max(pop_temp, key=lambda item: item.get('flag'))
        from spider.models import Popular_video
        Popular_video.objects.filter(status='A').update(**{'status': 'D'})
        popular = Popular_video()
        popular.url = result.get('url')
        popular.up_rate = result.get('flag')
        popular.save()


def save_table_for_charts():
    import json
    import operator
    videos = []
    # t_videos = Videos.objects.filter(status='A').values('url').annotate(c_url=Count('url')).all()

    t_videos = Videos.objects.filter(status='A').order_by('-crawling_time').all()
    url_maps = {}
    for i, video in enumerate(t_videos):
        if video.url not in url_maps.keys():
            url_maps.update({video.url: (len(videos), 1)})
            videos.append(video)
        else:
            url_maps.update({video.url: (url_maps.get(video.url)[0], url_maps.get(video.url)[1]+1)})

    sorted_result = sorted(url_maps.iteritems(), key=operator.itemgetter(1), reverse=False)

    result = []
    for url, value in sorted_result:
        index = value[0]
        video = videos[index]
        result.append(
            (
                index+1,
                video.title,
                video.playcount,
                value[1],
                url,
                video.site.ch_name,
                video.thumbnail
            )
        )

    f = open(commvals.TABLE_FOR_CHARTS, 'w')
    f.write(json.dumps(result))
    f.close()


def config(flag):
    import re
    f = open(commvals.RESOURCES_DIR + 'config.conf', 'r')
    get = f.read()
    if flag == 'thread_num':
        out = re.findall(re.compile(r'thread_num=(\d*)'), get)[0]
    elif flag == 'interval_time':
        out = re.findall(re.compile(r'interval_time=(\d),(\d),(\d),(\d)'), get)[0]
    elif flag == 'open_dev_web_server':
        out = re.findall(re.compile(r'open_dev_web_server=(\w*)'), get)[0]
    elif flag == 'start_time':
        out = re.findall(re.compile(r'start_time=(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)'), get)[0]
    else:
        out = ''
    return out


def get_page_count(table):
    count = len(table)
    return count / 10 + (1 if count % 10 != 0 else 0)


def get_page(table, page):
    page_count = get_page_count(table)
    result = []
    has_next = True
    if 1 <= page <= page_count:
        start = 1 + 10 * (page - 1)
        end = 10 + 10 * (page - 1)
        if end > len(table):
            end = len(table)
            has_next = False

        for i in range(start, end+1):
            result.append(table[i-1])
    return result, has_next, page_count


def get_table_by_site(table, site_id):
    # f = open(commvals.TABLE_FOR_CHARTS, 'r')
    # temp = f.read()
    # f.close()
    #
    # table = json.loads(temp)
    if site_id == -1:
        return table
    site = Sites.objects.filter(id=site_id).all()[0]
    result = []
    i = 1
    for item in table:
        if item[5] == site.ch_name:
            # result.append((i, item[1], item[2], item[3], item[4], item[5], item[6]))
            result.append((i,) + tuple(item[1:]))
            i += 1
    return result


def get_table_by_search(table, key_word):
    # f = open(commvals.TABLE_FOR_CHARTS, 'r')
    # temp = f.read()
    # f.close()
    #
    # table = json.loads(temp)
    if not len(key_word):
        return table
    result = []
    i = 1

    for item in table:
        if key_word in item[1]:
            # result.append((i, item[1], item[2], item[3], item[4], item[5], item[6]))
            result.append((i,) + tuple(item[1:]))
            i += 1

    return result


def readFile(fn, buf_size=262144):
    f = open(fn, "rb")
    while True:
        c = f.read(buf_size)
        if c:
            yield c
        else:
            break
    f.close()

if __name__ == '__main__':
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spiderx.settings")
    import django
    django.setup()
    # __add_date(['2015', '03', '22', '14', '45', '51'], ['1', '0', '0', '0'])
    # save_popular()
    f = open(commvals.TABLE_FOR_CHARTS, 'r')
    temp = f.read()
    f.close()
    import json
    table = json.loads(temp)
    # print get_page_count(table)
    # save_table_for_charts()
    # print get_page_count(table)
    # print len(table)
    # print get_page(table, get_page_count(table))
    # print get_table_by_site(1)
    # print get_table_by_search("优酷")
    # site = -1
    # search = ''
    # page = 1
    # f = open(commvals.TABLE_FOR_CHARTS, 'r')
    # temp = f.read()
    # f.close()
    # page_now = page
    # table = json.loads(temp)
    # table = get_table_by_site(table, site)
    # table = get_table_by_search(table, search)
    # page, has_next, page_count = get_page(table, page_now)
    # print page
    # print has_next
    # print page_count
    save_table_for_charts()