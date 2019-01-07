
from __future__ import absolute_import, unicode_literals
from celery import Celery

app = Celery('dreamhub_worker',
             broker='redis://localhost:6379/0',
             backend='redis://localhost:6379/0',
             include=['dreamhub.publisher.tasks','dreamhub.sniffer.tasks'])
app.conf.task_default_queue = 'default'
CELERY_ROUTES = {
    '*sniff*': {'queue': 'sniffer'},
    '*publish*': {'queue': 'publisher'},
}

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
)

import time
if __name__ == '__main__':
    app.start()
