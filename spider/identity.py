# coding:utf8
__author__ = 'Baxter'
from singleton import singleton


@singleton
class Identity():
    ids = []

    def __init__(self):
        pass

    def identity(self, ip):
        if ip in self.ids:
            return True
        else:
            return False