#coding:utf8
__author__ = 'Baxter'
import xlwt


class ExcelWriter():
    def __init__(self, path, titles, data):
        self.path = path
        self.data = data
        self.titles = titles
        self.excel = xlwt.Workbook()

    def write(self):
        sheet = self.excel.add_sheet('default')
        self.__write_title(sheet)
        for i, row_data in enumerate(self.data):
            row = sheet.row(i+1)
            self.__write_row(row, row_data)

        self.excel.save(self.path)

    def __write_row(self, row, row_data):
        for i, cell in enumerate(row_data):
            row.write(i, cell)

        return None

    def __write_title(self, sheet):
        for i, title in enumerate(self.titles):
            sheet.write(0, i, title)


if __name__ == '__main__':
    import sys
    import os
    sys.path.append('C:/Users/Baxter/Desktop/spiderx')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spiderx.settings")
    import django
    django.setup()
    from spider.models import Videos
    # videos = Videos.objects.filter(status='A').all()
    videos = Videos.objects.raw("select * from spider_videos, spider_sites where spider_videos.site_id=spider_sites.id AND spider_videos.status='A';")
    # sites = Sites.objects.all()
    titles = ['No.', u'标题', u'来源', u'点击量', u'收藏', u'评论', u'赞', u'踩', u'网址']

    import time
    start = time.time()
    data = [(i+1,
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
    # print 'get time:', time.time() - start
    # ExcelWriter('test.xls', titles, data).write()
    # print time.time() - start
    from spider.api import get_page, get_table_by_search, get_table_by_site
    page_now = 1
    table = get_table_by_site(data, int(1))
    table = get_table_by_search(table, "优酷")
    page, has_next, page_count = get_page(data, page_now)
    # print page
    # print has_next
    # print page_count
    import json
    print json.dumps({'result': page,
                       'has_next': has_next,
                       'has_pre': page_now != 1,
                       'page_total': page_count,
                       'page_now': page_now})