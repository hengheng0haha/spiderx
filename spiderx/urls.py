from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from dajaxice.core import dajaxice_autodiscover, dajaxice_config
dajaxice_autodiscover()
urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'spiderx.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'spider.views.index', name='index'),
    url(r'^index/', 'spider.views.index'),
    url(r'^manage/', 'spider.views.manage'),
    url(r'^charts/', 'spider.views.charts'),
    url(r'^test/', 'spider.views.test'),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_PATH}),
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
    url(r'^ranking_list/', 'spider.views.ranking_list'),
    url(r'^tables/', 'spider.views.tables'),
    url(r'^download_excel/', 'spider.views.download_excel'),
)
