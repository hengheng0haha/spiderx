# coding:utf8
from django.shortcuts import render, render_to_response
from spider.models import Videos, Sites, Snapshots
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
# Create your views here.


def index(req):
    return render_to_response('index.html', {})


def test(req):
    return render_to_response('test.html', {})


def manage(req):
    from identity import Identity
    import commvals
    import status
    import hashlib

    s = status.Status()
    t = Identity()
    resp = dict()
    if req.POST:
        passwd = req.POST.get('password')
        if hashlib.md5(passwd.encode('utf-8')).hexdigest() == commvals.SERVER_PASSWORD:
            t.ids.append(req.META.get('REMOTE_ADDR'))
            resp.update({'identity': True})
        else:
            resp.update({'identity': False})
    else:
        if t.identity(req.META.get('REMOTE_ADDR')):
            resp.update({'identity': True})
        else:
            resp.update({'identity': False})
    return render_to_response('manage.html', resp)


def charts(req):
    cols = ['No.', '标题', '最高点击量(次)', '首页出现数(次)', '来源', '查看图表']

    import os
    import spider.commvals as commvals

    if not os.path.exists(commvals.TABLE_FOR_CHARTS):
        from spider.api import save_table_for_charts
        save_table_for_charts()

    sites = Sites.objects.all()
    return render_to_response('charts.html', {'cols': cols, 'sites': sites})


def ranking_list(req):
    return render_to_response('ranking_list.html', {})


def tables(request):
    cols = ['No.', '标题', '来源', '获取时间', '点击量', '收藏', '评论', '赞', '踩']
    sites = Sites.objects.all()
    return render_to_response('tables.html', {'cols': cols, 'sites': sites})


def download_excel(req):
    import os
    from spider.api import generate_id
    from spider.excel import ExcelWriter
    filename = generate_id() + '.xls'
    print req
    titles = ['No.', u'标题', u'获取时间',  u'点击量', u'收藏', u'来源', u'评论', u'赞', u'踩', u'网址']
    videos = Videos.objects.raw("select * from spider_sites, spider_videos where spider_videos.site_id=spider_sites.id AND spider_videos.status='A';")
    data = [(i+1,
             video.title,
             video.crawling_time.strftime('%Y-%m-%d %H:%M:%S'),
             video.playcount,
             video.favorite,
             video.ch_name,
             video.community,
             video.upcount,
             video.downcount,
             video.url) for i, video in enumerate(videos)]
    if req.GET:
        from spider.api import get_table_by_site, get_table_by_search, get_page
        data = get_table_by_site(data, int(req.GET.get('site')[0])) if len(req.GET.get('site')) else data
        data = get_table_by_search(data, req.GET.get('search')[0]) if len(req.GET.get('search')) else data
        data, has_next, page_count = get_page(data, int(req.GET.get('page')[0]))
    ExcelWriter(filename, titles, data).write()
    wrapper = FileWrapper(open(filename, 'rb'))
    response = HttpResponse(wrapper, content_type='text/plain')
    response['Content-Length'] = os.path.getsize(filename)

    return response