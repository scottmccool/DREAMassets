from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery.signals import worker_ready

from dreamhub.publisher.tasks import publish_observation
from dreamhub.sniffer.tasks import sniff
#from dreamhub.publisher.tasks import publish
#from dreamhub.sniffer.tasks import sniff

app = Celery("dreamhub",
             broker='redis://localhost:6379/0',
             backend='redis://localhost:6379/0'
)

app.conf.timezone = 'UTC'

# # Start a sniffer with default arguments every minute
# app.conf.beat_schedule = {
#     'sniff-every-minute': {
#         'task': 'dreamhub.sniffer.tasks.sniff_new',
#         'schedule': 60.0
#     },
# }


# Run the worker
if __name__ == '__main__':
    app.start()
