Lucid is a simplified celery-based sniffer+publisher system

It's not complete.

Orchestrate edge processing with celery tasks
Requires a local redis server
Ships dreamhub python module which contains a celery app (pointed at localhost redis)
  tasks:
    sniffer.sniff -> Read BTLE ads, find fujitsu tags, call publisher.publish with match
    publisher.publish -> Write sensor tag to google cloud pubsub topic
Dreamhub python module also contains a helper script to submit scan requests forever (should this be embedded in the worker app?)
  $ python3 minder.py


It's currently missing a bunch of helper scripts, but you can:
# Install the prerequisites
```
$ pip3 install flower
$ pip3 install -r requirements.txt
$ sudo docker run --net=host redis 
```

# Run a celery worker on all queues
```
$ celery -A dreamhub.celery worker --loglevel info -Q default,sniffer,publisher
```
# Run a helper script which will submit sniff requests forever
```
$ python3 minder.py
```

# Install flower and monitor message flow
```
$ pip3 install flower
$ flower -b redis://localhost/0 --results-backend='redis://localhost/0'
```
(See http://localhost:5555/ for a UI)
