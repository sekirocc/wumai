from flask import Flask
import werkzeug.serving
import signal
import gevent
from gevent.wsgi import WSGIServer
# import logging


class Service():

    def __init__(self, debug=True):
        self.debug = debug

        service = Flask(__name__)

        self.service = service

    def register(self, blueprint, prefix=''):
        self.service.register_blueprint(blueprint, url_prefix=prefix)

    def start(self, bind='0.0.0.0', port=9000):
        http_server = WSGIServer((bind, port), self.service)

        def runServer():
            print('start server...')
            http_server.serve_forever()
        if self.debug:
            runServer = werkzeug.serving.run_with_reloader(runServer)

        def stopServer():
            print('shutdown server gracefully...')
            http_server.stop(timeout=60)
            exit(signal.SIGTERM)

        gevent.signal(signal.SIGTERM, stopServer)

        runServer()

        # if not self.debug:
        #     logFormatter = logging.Formatter(
        #         '%(asctime)s\t[%(levelname)s]\t%(message)s')
        #     fileHandler = logging.FileHandler('/log/%s.log' % port)
        #     fileHandler.setFormatter(logFormatter)
        #     self.service.logger.addHandler(fileHandler)
