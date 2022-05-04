import sys
from gevent import monkey
from wumai import config
from wumai import db
from wumai import cache

GEVENT = False


def init():
    reload(sys)
    sys.setdefaultencoding('utf-8')

    if config.CONF.db_host:
        db.setup()

    if config.CONF.redis_host:
        cache.setup()

    if config.CONF.gevent:
        global GEVENT
        GEVENT = True

        # flask's auto loader
        # http://flask.pocoo.org/snippets/34/
        monkey.patch_all()
