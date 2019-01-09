# Data terminology:
#   BLE Advertisement --> Bluepy snatches these out of the air, like magic!
#   packet --> A python dictionary containing data extracted from the advertisement and metadata added by the lucid frameowrk

# Data flow
## <BLE Advertisement> !! -> sniffer -> <sniffed_packets queue>
##  <sniffed_packets_queue> -> publisher -> <google cloud function>

# Sniffer runs a thread per HCI detected, forever.  Assume systemd will restart on error.
# Publisher has basic filtering and batching logic.
# Both are managed as celery tasks from the minder
from __future__ import absolute_import, unicode_literals
from celery import shared_task

# Builtins
import time
import re
import base64
import json
import socket
import os

from dreamhub.sniffer import ble_sniffer

# Gather data from hub, it is assumed sniff will publish readings
@shared_task(rate_limit=1)
def sniff(hci=0):
    ble_sniffer.sniffForever(hci)