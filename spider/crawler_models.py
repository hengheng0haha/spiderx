# coding:utf8
__author__ = 'Baxter'


class Url():
    def __init__(self, url='', url_tip='', url_type='', id_indb=None):
        self.url = url

        # @url_tip in config.sites
        self.url_tip = url_tip

        # @url_type in ('host', 'video')
        self.url_type = url_type

        self.id_indb = id_indb

    def __str__(self):
        import chardet

        try:
            return u'url:%s, url_tip:%s, url_type:%s, id_indb:%s' % (self.url.replace('&', ' ').replace(';', ''),
                                                                     self.url_tip,
                                                                     self.url_type,
                                                                     str(self.id_indb))
        except UnicodeDecodeError, e:
            pass


class Response():
    """
    crawler response model
    """

    def __init__(self, response='', c_type='', url=''):
        self.response = response
        self.content_type = c_type
        self.url = url

    def __str__(self):
        return self.r_type