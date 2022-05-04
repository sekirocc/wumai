## Installation

```
yum install wumai
```

## Usage


### step 1. define routes in dict form.

```
def handler():
    return {'text': 'hello world'}

routes = {
    'ActionName': handler,
}
```

### step 2. setup app_root and log_dir, 

```
from wumai import config

config.CONF.apply(**{
    'app_root': os.path.dirname(os.path.abspath(__file__)),
    'log_dir': '/var/log/example'
})
```

### step 3. create server and start with port.

```
from wumai.server import create_api

api = create_api('public', debug=True)
api.route(routes)
api.start(port=8080)
```

## Detail


### Server Types

there are two server types: api, worker.

- `api` server can accept http POST,
- `worker` server is a looping server to fetch and execute jobs.

example:

create a worker and start it.

```
from wumai.server import create_worker
from wumai import config

config.CONF.apply(**{
    'app_root': os.path.dirname(os.path.abspath(__file__)),
    'log_dir': '/var/log/example'
})

worker = create_worker(pick_size=10,
                       exec_size=10,
                       exec_timeout=600,
                       gevent=True)
worker.start()
```

the worker will run forever. fetch some jobs every 2 seconds,
spawn a greenlet to execute each of these jobs.

### Configuration

Settings in `wumai` must be set to a global variable `CONF` in `wumai.config` module. 
You can modify this var directly, but invoke its `apply` api is recommended.

```
from wumai import config

settings = {
    'app_root': '/var/www/example',
    'log_dir': '/var/log/example'
}

config.CONF.apply(**settings)
```

`app_root` & `log_dir` are required to be set.

There are some configs, but is not required to use `wumai`.

#### DB config
If you use models shipped with `wumai`, you should config database to let `wumai` to access for
mapping db records to models.

| name | os env name | default |
| ---- | ----------- | ------- |
| host | DB_HOST  | None  |
| port | DB_PORT  | 3306  |
| user | DB_USER  | None  |
| password | DB_PASSWORD  | None  |
| database | DB_DATABASE  | None  |


#### Worker config
Worker server is periodicaly fetching jobs and execute them.

By default setting:

* worker picks 10 jobs every 2 seconds and put them to a thread pool.

* thread pool excute size is 10, which means at a time there are at most 10 jobs running.

* if job is running more than 10 munites, it failed as timeout.

`create_worker(pick_size, exec_size, exec_timeout, gevent)`

| name | description | default |
| ---- | ----------- | ------- |
| pick_size | how many job to pick from db every loop(2 seconds) | 10 |
| exec_size | worker threads running pool size | 10 |
| exec_timeout | every job execution timeout | 600 |
| gevent | the worker thread is using geventlet | True |

Note:
    by now, gevent is the only thread manager. so make sure pass `gevent=True` to `create_worker`.


#### Custom configs

All you need to do is import and modify the global object `CONF` from `wumai.config`.

```
from wumai import config

config.CONF.apply(**{
    'op_keystone_endpoint': 'http://localhost:6257/v3',
    'op_admin_name': 'admin',
    'op_admin_pass': 'pass'
})
```

### Models

There are two kinds of models delivered with `wumai` by default. They are convinient and maybe
used by vary projects.

Note:
    If you want use these models, you should:
    * 1. prepare database and tables by yourself, table name and fields name are describe below.
    * 2. supply database configration to `wumai` through environ variables.

#### job model

table_name: `job`

| field name | type |
| ---- | ---- |
| id |  varchar(32) |
| project_id | string(32) |
| action | string(50) |
| status | string(10) (enum: running, pending, finished, error)|
| error | text |
| result | text |
| params | text |
| updated | datetime |
| created | datetime |
| run_at | datetime |
| try_period | integer |
| try_max | integer |
| trys | integer |

#### operation model


### Content-Type

json is the only supported Content-Type.
request body are parsed by json.loads, response will be serialized by json.dumps

### Request

in action handler, you can access the following attributes from request

```
import flask

print flask.request.action  # ===> action name,
print flask.request.params  # ===> a dict parsed from request body, using `json.loads`
```

request body must be a valid json string, and the json must contain `action` field.

```
{
    'action': 'DescribeInstances',
    ... other params ...
}
```


### Response

handler should return a dict. which will be serialized by json.dumps, then sent as response.


### Logger

logs are stored in file, rotated by day.

every server(api, worker) has three kinds of logs, they are

| type | file | description |
| -----| ---- | ------|
| normal | normal.log  | app logger, the default logger used by your app. |
| access | access.log  | framework level logger, log user access, not controlled by your app.  |
| db | db.log  | framework level logger, log sql activities. |

most time, when you get logger from framework, you get the normal log.

```
from wumai import logger

logger.info('some info message')
logger.debug('some debug message')
logger.error('some error message')
logger.warning('some warning message')

```
default logger is named the `root` logger, but in specific situation,
you'd better use root logger's children, the `child` logger,
which will prepend extra message in log record, so that you can know where the message come from.

```
from wumai import logger
logger = logger.getChild(__file__)

logger.info('some info message')
```

default normal logger format:

```
[LOGGER NAME][%(levelname)s][%(asctime)s][%(contextId)s][%(name)s] %(message)s
```
it's built in framework, changing log format is unsupported.


### Context

as shown in logger format, there is a field `contextId`, which is a thread context id.
because our server is running at parallel(gevent-based) situation,
it's usefull to know what context we are in.
you can do this through `local` module

```
from wumai.common import local

context_id = local.get_context_id()
```

NOTICE:
in most time, app should not need to care about context,
unless you want to store and access some value globally (which is a bad practice).



### Error

`wumai` already handled a large number of exceptions, when it catches these exceptions, it will identify them,
contruct response to user with relative error code and message.

in your app, you can raise these supported exceptions.

| exception name | error code  |
| ----- | ---- |
|iaas_error.IaasProviderActionError | 5001 |
|iaas_error.ActionsPartialSuccessError | 5001 / 5002 |
|iaas_error.InvalidRequestParameter | 4100 |
|iaas_error.ResourceNotFound | 4104 |
|iaas_error.ResourceNotBelongsToProject | 4103 |
|iaas_error.ResourceActionForbiden |4105  |
|iaas_error.ResourceActionUnsupported | 4106 |
|iaas_error.ResourceIsBusy | 4105 |
|project_error.ResourceQuotaNotEnough | 4113 |
|project_error.ProjectDuplicated | 4600 |
|project_error.ProjectNotFound | 4604 |
|project_error.AccessKeyExpired | 4101 |
|project_error.AccessKeyInvalid | 4101 |
|project_error.ManageAccessKeyInvalid | 4601 |
|project_error.AccessKeyNotFound | 4614 |
|project_error.AccessKeyDuplicated | 4611 |




### Notify

when worker server executing a job and failed, it will send notifications to notify channels.
currently `wumai` support two kinds of notify channel, if you set OS env variables correctly.

#### Slack

worker try to send to slack if you have `SLACK_WEBHOOK_URL` set, if not set, worker ignore it.

#### SMS

worker try to send to plato-devops sms if you have the following env vas set, worker ignore it.
`NOTIFY_SMS_UR`
`NOTIFY_SMS_KEY`
`NOTIFY_SMS_SECRET`
`NOTIFY_SMS_MOBILES`

### Sql and Migration

`wumai` doesnot support sql migration. you have to prepared database before running server.
we doesnot care what method you using when populate your database table structure.

there are too kinds of model pre-defined:

* Job model
* Resource model

Job model is used by worker server, so when worker server starts, it will check `job` table
and try to fetch data from the table, and feed jobs in to Job model, which should has the 
following structure:

| field name | type |
| ---- | ---- |
| id |  varchar(32) |
| project_id | string(32) |
| action | string(50) |
| status | string(10) (enum: running, pending, finished, error)|
| error | text |
| result | text |
| params | text |
| updated | datetime |
| created | datetime |
| run_at | datetime |
| try_period | integer |
| try_max | integer |
| trys | integer |

Resource model, on the contrast, is just a regular base class for resources (Instance,
for example), which provides handy methods you may use for your logic, such as:

* `must_belongs_project(project_id)` a method raise exception if the resource doesnot belongs
to the project.  
* `is_busy()` return True if current resource is ended with `-ing`

If you have a model and decided to subclass this Resource model, the database table correponding
to model should at least has the following fields:

| field name | type |
| ---- | ---- |
| id |  varchar(32) |
| project_id | string(32) |
| status | string(10) |

these fields are used by those handy methods above. so make sure they exists before using them.
