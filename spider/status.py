# coding:utf8
__author__ = 'Baxter'
import time
from spider.models import Server_status, SERVER_STATUS_CHOICE
import threading
import random

STATUS_RUNNING = 0
STATUS_WAITING = 1
STATUS_STOPPED = 2


class Status():
    def __init__(self):
        pass

    def status(self, s):
        s_status = Server_status.objects.filter(status='A').all()
        if not len(s_status):
            temp_status = Server_status()
            temp_status.server_status = SERVER_STATUS_CHOICE[s][0]
            temp_status.save()
        elif s == 2:
            import datetime
            stop_time = datetime.datetime.now()
            update = {'server_status': 'S',
                      'status': 'D',
                      'stop_time': stop_time,
                      'run_time': (stop_time - s_status[0].start_time).seconds}
            s_status.update(**update)
        else:
            update = {'server_status': SERVER_STATUS_CHOICE[s][0]}
            s_status.update(**update)

    def get_status(self):
        temp_status = Server_status.objects.filter(status='A').all()
        if not len(temp_status):
            return SERVER_STATUS_CHOICE[2][0]
        else:
            return temp_status[0].server_status

    def compare(self, s):
        return self.get_status() == SERVER_STATUS_CHOICE[s][0]

    def ncompare(self, s):
        return self.get_status() != SERVER_STATUS_CHOICE[s][0]


class Test(threading.Thread):
    def __init__(self, i):
        super(Test, self).__init__()
        self.thread_num = i

    def run(self):
        s = Status()
        while True:
            t = random.randrange(0, 3)
            print str(t) + '!!!' + str(self.thread_num)
            s.status(t)
            print s.get_status() + str(self.thread_num)
            time.sleep(1)

if __name__ == '__main__':
    import sys
    import os
    sys.path.append('C:/Users/Baxter/Desktop/spiderx')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spiderx.settings")
    import django
    django.setup()

    threads = [Test(i) for i in range(5)]
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
