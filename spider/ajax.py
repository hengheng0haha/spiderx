# coding:utf8
__author__ = 'Baxter'
import json
from dajaxice.decorators import dajaxice_register
from spider.models import Videos, Sites, Server_status, Popular_video


def cal(a, b):
    return a.playcount - b.playcount


def all_zero(a):
    return a.count(0) == len(a)


@dajaxice_register
def show_chart(request, title):
    videos = Videos.objects.filter(status='A').filter(title=title).all()
    maps = {
        'playcount': {'name': '播放数', 'data': [video.playcount for video in videos]},
        'community': {'name': '评论数', 'data': [video.community for video in videos]},
        'favorite': {'name': '收藏数', 'data': [video.favorite for video in videos]},
        'upcount': {'name': '赞', 'data': [video.upcount for video in videos]},
        'downcount': {'name': '踩', 'data': [video.downcount for video in videos]},
    }
    result = {
        'title': title,
        'source': videos[0].site.url,
        'xAxis': [str(video.crawling_time) for video in videos],
    }
    for key, value in maps.items():
        result.update({key: [value]})
    return json.dumps(result)


@dajaxice_register
def popular(request):
    pop = Popular_video.objects.filter(status='A').all()
    if not len(pop):
        return ''
    pop = pop[0]
    videos = Videos.objects.filter(status='A', url=pop.url).order_by('crawling_time').all()
    maps = {
        'playcount': {'name': '播放数', 'data': [video.playcount for video in videos]},
        'community': {'name': '评论数', 'data': [video.community for video in videos]},
        'favorite': {'name': '收藏数', 'data': [video.favorite for video in videos]},
        'upcount': {'name': '赞', 'data': [video.upcount for video in videos]},
        'downcount': {'name': '踩', 'data': [video.downcount for video in videos]},
    }
    result = {
        'title': videos[0].title,
        'source': videos[0].site.url,
        'xAxis': [str(video.crawling_time) for video in videos],
        'url': videos[0].url,
    }
    for key, value in maps.items():
        result.update({key: [value]})
    return json.dumps(result)


@dajaxice_register
def server_manager(req, commd):
    import work
    from spider.models import Server_status

    result = {}
    if commd == 'get':
        pass
    elif commd == 'stop':
        work.server_stop()
    elif commd == 'restart':
        work.server_restart()
    elif commd == 'start':
        work.server_restart()

    m_status = Server_status.objects.filter(status='A').all()
    if len(m_status):
        ss = m_status[0].server_status
    else:
        ss = 'S'
    result.update({'result': ss})
    import json
    return json.dumps(result)


@dajaxice_register
def ranking_list(req, m_type):
    from spider.api import load_ranking_list
    l = load_ranking_list(m_type)
    return json.dumps({'result': l})


@dajaxice_register
def get_next_time(req):
    from spider.api import load_next_start_time
    next_time = map(int, list(load_next_start_time()))
    result = json.dumps({'result': next_time})
    return result


@dajaxice_register
def get_table_with_page_site_search(req, page, site, search, type):
    from spider.api import get_page, get_table_by_search, get_table_by_site
    import spider.commvals as commvals
    if type == 'charts':
        f = open(commvals.TABLE_FOR_CHARTS, 'r')
        temp = f.read()
        f.close()
        table = json.loads(temp)
    else:
        videos = Videos.objects.raw("select * from spider_sites, spider_videos where spider_videos.site_id=spider_sites.id AND spider_videos.status='A';")
        table = [(i+1,
                 video.title,
                 video.crawling_time.strftime('%Y-%m-%d %H:%M:%S'),
                 video.playcount,
                 video.favorite,
                 video.ch_name,
                 video.community,
                 video.upcount,
                 video.downcount,
                 video.url,
                 video.thumbnail) for i, video in enumerate(videos)]
    page_now = page
    table = get_table_by_site(table, int(site))
    table = get_table_by_search(table, search)
    page, has_next, page_count = get_page(table, page_now)

    return json.dumps({'result': page,
                       'has_next': has_next,
                       'has_pre': page_now != 1,
                       'page_total': page_count,
                       'page_now': page_now})