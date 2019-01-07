# The controller which manages celery tasks for sniffer and publisher

import dreamhub.celery
import time
import datetime

# Run in a loop, firing off sniffer tasks
while True:
    print("%s: Starting sniffer task in foreground" % datetime.datetime.utcnow())
    try:
        published,skipped = dreamhub.celery.app.send_task('sniffer.sniff').get(timeout=20)
        print("%s: Scan complete, published: %d, skipped: %d adverts." % (datetime.datetime.utcnow(), published,skipped))
    except Exception as e:
        print("%s: Sniffer exited with exception:\n%s"%(datetime.datetime.utcnow(),format(e)))
    time.sleep(1.0)
