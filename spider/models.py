from django.db import models

# Create your models here.


STATUS_CHOICE = (
    (u'A', u'Active'),
    (u'D', u'Deleted'),
    (u'B', u'Building'),
)

SERVER_STATUS_CHOICE = (
    (u'R', u'Running'),
    (u'W', u'Waiting'),
    (u'S', u'Stopped'),
)


class Sites(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField(max_length=200)
    ch_name = models.CharField(max_length=200, default='None')
    status = models.CharField(max_length=45, default='A', choices=STATUS_CHOICE)

    def __unicode__(self):
        return '[%s]%s' % (self.name, self.status)


class Videos(models.Model):
    title = models.TextField(max_length=500)
    site = models.ForeignKey(Sites)
    playcount = models.IntegerField(default=0)
    thumbnail = models.FilePathField(max_length=200)
    crawling_time = models.DateTimeField(auto_now_add=True)
    favorite = models.IntegerField(default=0)
    community = models.IntegerField(default=0)
    upcount = models.IntegerField(default=0)
    downcount = models.IntegerField(default=0)
    url = models.URLField(max_length=200)
    status = models.CharField(max_length=45, default='B', choices=STATUS_CHOICE)

    def __unicode__(self):
        return '[%s]%s' % (self.title, self.status)


class Snapshots(models.Model):
    path = models.FilePathField(max_length=200)
    site = models.ForeignKey(Sites)
    get_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=45, default='A', choices=STATUS_CHOICE)

    def __unicode__(self):
        return 'site: %s, path: %s, get_time: %s, status: %s' % (self.site, self.path, self.get_time, self.status)


class Server_status(models.Model):
    server_status = models.CharField(max_length=45, default='S', choices=SERVER_STATUS_CHOICE)
    start_time = models.DateTimeField(auto_now_add=True)
    stop_time = models.DateTimeField(blank=True)
    run_time = models.IntegerField(default=0)
    status = models.CharField(max_length=45, default='A', choices=STATUS_CHOICE)

    def __unicode__(self):
        return 'Server status :' + self.server_status


class Popular_video(models.Model):
    url = models.URLField(max_length=200)
    up_rate = models.IntegerField(default=0)
    status = models.CharField(max_length=45, default='A', choices=STATUS_CHOICE)

    def __unicode__(self):
        return "Popular video url :" + self.url + ' status :' + self.status