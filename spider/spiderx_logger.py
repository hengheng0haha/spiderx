__author__ = 'Baxter'
# coding:utf8
import logging
import logging.config


def logger():
    import commvals
    logging.config.fileConfig(commvals.LOGGER_CONFIG_CONF)
    log = logging.getLogger(commvals.LOGGERS[commvals.LOGGER_DEBUG_DEBUG])
    return log

if __name__ == '__main__':
    logger = logger()
    logger.debug('debug test')
    logger.info('info test')
    logger.warning('warning test')
    logger.error('error test')