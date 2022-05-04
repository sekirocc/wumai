import inspect
import six
import copy
import traceback

from wumai import version

from oslo_utils import encodeutils
from oslo_config import cfg


class MissingArgs(Exception):
    def __init__(self, missing):
        self.missing = missing
        msg = 'Missing arguments: %s' % ', '.join(missing)
        super(MissingArgs, self).__init__(msg)


def validate_args(fn, *args, **kwargs):
    argspec = inspect.getargspec(fn)

    num_defaults = len(argspec.defaults or [])
    required_args = argspec.args[:len(argspec.args) - num_defaults]

    if getattr(fn, '__self__', None):
        required_args.pop(0)

    missing_required_args = required_args[len(args):]
    missing = [arg for arg in missing_required_args if arg not in kwargs]
    if missing:
        raise MissingArgs(missing)


def args(*args, **kwargs):
    def _decorator(func):
        func.__dict__.setdefault('args', []).insert(0, (args, kwargs))
        return func
    return _decorator


def alias(command_name):
    def _decorator(func):
        func.alias = command_name
        return func
    return _decorator


def _method_of(cls):
    all_methods = inspect.getmembers(
        cls, predicate=lambda x: inspect.ismethod(x) or inspect.isfunction(x))
    methods = [m for m in all_methods if not m[0].startswith('_')]
    return methods


def _add_command_parsers(categories, subparsers):
    parser = subparsers.add_parser('version')
    # parser = subparsers.add_parser('bash-completion')
    # parser.add_argument("query_category", nargs="?")

    for cmd in categories.types():
        command_object = categories.get(cmd)
        parser = subparsers.add_parser(cmd, description='TODO')
        parser.set_defaults(command_object=command_object)

        category_subparsers = parser.add_subparsers(dest='action')
        for method_name, method in _method_of(command_object):
            parser = category_subparsers.add_parser(
                getattr(method, 'alias', method_name),
                description='TODO')
            action_kwargs = []
            for args, kwargs in getattr(method, 'args', []):
                args = copy.copy(args)
                kwargs = copy.copy(kwargs)

                action_kwargs.append(kwargs['dest'])
                kwargs['dest'] = 'action_kwarg_' + kwargs['dest']

                parser.add_argument(*args, **kwargs)

            parser.set_defaults(action_fn=method)
            parser.set_defaults(action_kwargs=action_kwargs)
            parser.add_argument('action_args', nargs='*')


def parse(argv, categories):
    conf = cfg.ConfigOpts()
    handler = lambda subparsers: _add_command_parsers(categories, subparsers)  # noqa
    category_opt = cfg.SubCommandOpt('category',
                                     title='Command categories',
                                     help='Available categories',
                                     handler=handler)
    conf.register_cli_opt(category_opt)

    try:
        conf(argv, project='wumai_cliutils', version=version.version_string())
    except Exception:
        raise Exception('arguments %s can not be parsed' % argv)

    return conf


def run(conf):
    if conf.category.name == 'version':
        print(version.version_string())
        return(0)

    fn = conf.category.action_fn
    fn_args = [encodeutils.safe_encode(arg)
               for arg in conf.category.action_args]
    fn_kwargs = {}
    for k in conf.category.action_kwargs:
        v = getattr(conf.category, 'action_kwarg_' + k)
        if v is None:
            continue
        if isinstance(v, six.string_types):
            v = encodeutils.safe_encode(v)
        fn_kwargs[k] = v

    try:
        validate_args(fn, *fn_args, **fn_kwargs)
    except MissingArgs as ex:
        print(ex)
        return(1)

    try:
        ret = fn(*fn_args, **fn_kwargs)
        return(ret)
    except Exception as ex:
        stack = traceback.format_exc()
        print(stack)
