# coding:utf8
import os
import spiderx.settings
__author__ = 'Baxter'

APP_DIR = os.path.dirname(spiderx.settings.__file__)[:os.path.dirname(spiderx.settings.__file__).rindex('\\')]
RESOURCES_DIR = APP_DIR + '\\spider\\resources\\'
CRAWLER_CONFIG_XML = RESOURCES_DIR + 'crawler.xml'
DB_NAME = 'crawler'
LOGGER_CONFIG_CONF = RESOURCES_DIR + 'logger.conf'
LOGGER_DEBUG_DEBUG = 0
LOGGERS = ['logger1']
SERVER_PASSWORD = 'e10adc3949ba59abbe56e057f20f883e'
SNAPSHOTS_DIR = APP_DIR + '\\spider\\snapshots\\'
TABLE_FOR_CHARTS = RESOURCES_DIR + 'table_for_charts.txt'