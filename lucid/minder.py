# Supervisor thread for making sure there is always a sniffer task running

import time
import datetime
from dreamhub import celery

# Run in a loop, firing off sniffer tasks
while True:
    print("%s: Starting sniffer task in foreground" % datetime.datetime.utcnow())
    try:
        ar=celery.app.send_task('dreamhub.sniffer.tasks.sniff').wait()
        print("%s: Sniffer call returned without error. (%s)" %(datetime.datetime.utcnow(),ar.get()))
    except Exception as e:
        print("%s: Sniffer exited with exception:\n%s"%(datetime.datetime.utcnow(),format(e)))
    time.sleep(1.0)
