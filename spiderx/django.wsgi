import os, sys  
import django.core.handlers.wsgi  
sys.path.append('C:/Users/Baxter/Desktop/spiderx')  
os.environ['DJANGO_SETTINGS_MODULE'] = 'spiderx.settings'  
application = django.core.handlers.wsgi.WSGIHandler()