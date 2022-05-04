import functools

from wumai.model import base
from wumai.model.job import job as job_model
from wumai.common import local
from wumai.common import utils
from wumai import db

from wumai import logger
logger = logger.getChild(__file__)


def job_id_context(method):
    @functools.wraps(method)
    def wrap(job_id, *args, **kwargs):
        local.start_context(job_id[-4:])
        try:
            return method(job_id, *args, **kwargs)
        finally:
            local.clear_context()
    return wrap


@job_id_context
@utils.footprint(logger)
def run_job(job_id, worker):
    with base.open_transaction(db.DB):
        job = job_model.fetch(job_id)

        if not job or not job.status_executable():
            status = job['status'] if job else 'db locked'
            logger.info('not executable right now, status: (%s).' % status)
            return

        job_model.prepare(job)

    job = job_model.fetch(job_id)
    job_model.execute(job, worker=worker)


@job_id_context
@utils.footprint(logger)
def clean_job(job_id):
    """
    fetch a job lock. update the job status to pending
    """
    with base.open_transaction(db.DB):
        job = job_model.fetch(job_id)

        if not job or not job.status_resetable():
            status = job['status'] if job else 'db locked'
            logger.info('not clean right now, status: (%s).' % status)
            return

        job_model.reset(job)
