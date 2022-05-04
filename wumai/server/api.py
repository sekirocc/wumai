import flask
from wumai import bootstrap
from wumai import logger

from wumai.common.service import Service


def index():
    response_data = """\
It\'s Wumai API service.
"""
    response = flask.make_response(response_data, 200)
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return response


def make_call(routes):
    from wumai import web
    from wumai.web import ground

    @ground.handle
    @web.log_user_operation
    @web.guard_params_failure
    @web.load_action_params
    def call():
        action = flask.request.action
        if action in routes:
            return routes[action]()
        else:
            raise ground.HandleError('Unknow action %s.' % action, 4000)

    return call


def route_blueprint(routes):
    assert bool(routes), 'routes is empty!'

    handler = make_call(routes)

    blueprint = flask.Blueprint('iaas', __name__)

    blueprint.add_url_rule('/', 'index', index, methods=['GET'])
    blueprint.add_url_rule('/', 'handler', handler, methods=['POST'])

    return blueprint


class API(object):
    def __init__(self, debug=False):
        self.service = Service(debug=debug)

    def route(self, routes):
        self.service.register(route_blueprint(routes), prefix='')
        return self

    def start(self, port):
        # save app port in config
        from wumai import config
        config.CONF.apply(app_port=port)

        self.service.start(port=port)


def create_api(name, debug=False):
    from wumai.server import ensure_config_setup
    ensure_config_setup()

    bootstrap.init()
    logger.init(dirname=name)

    return API(debug)
