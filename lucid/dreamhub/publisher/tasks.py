from __future__ import absolute_import, unicode_literals
from celery import shared_task

import os
from dreamhub.publisher import gpub

#@app.task(base=Batches,flush_every=100, flush_interval=60)
@shared_task
def publish(payload):
    p = str(payload)
    f = open("/tmp/dreamhub_publisher_readings","a")
    f.write(p)
    f.write("\n")
    f.close()
    gpub.sendit(payload)
