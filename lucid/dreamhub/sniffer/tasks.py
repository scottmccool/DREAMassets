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

# Sniffer utilities
from bluepy.btle import Scanner, DefaultDelegate

# Sniff BLE advertisments, filter for fujitsu tag, and call publisher.publish on anything
# that matches.  Intended to be called from minder.py
from dreamhub.publisher.tasks import publish

@shared_task(rate_limit=1, timeout=60)
def sniff(hci=0, scantime=50):
    published = 0
    discarded = 0
    try:
        scanner = Scanner().withDelegate(DefaultDelegate())
        print("Scanning for %d seconds" % (scantime))
        devices = scanner.scan(float(scantime))
        fujitsu_packet = re.compile(r'010003000300')
        print("Filtering %d devices found during scan" % (len(devices)))
        for dev in devices:
            packet = extract_packet_from_bleAdvertisement(dev)
            if re.search(fujitsu_packet, packet['mfr_data']):
                print("Publishing packet: %s"%(packet))
                publish.app.send_task('dreamhub.publisher.tasks.publish', [packet], queue='publisher')
                published += 1
            else:
                discarded += 1
                print("Could not find fujitsu maufacturing string, discarding:\n%s"%(packet))
    except Exception as e:
        print("Exception in sniffer loop (%s), better luck next time (pub: %d, disc: %d)\n"%(e,published,discarded))
        print(e)
    return(published,discarded)

def extract_packet_from_bleAdvertisement(bleAdvertisement):
    packet = None
    try:
        # get the tag_id (MAC address) and rssi from the BLE advertisement
        # since the MAC address comes with colons, remove them.
        tag_id = bleAdvertisement.addr.replace(':', '')
        rssi = bleAdvertisement.rssi

        # getScanData returns a tripple from the ScanEntry object
        # the tripple has the advertising type, description and value (adtype, desc, value)
        triples = bleAdvertisement.getScanData()

        # Bluetooth defines AD types https://ianharvey.github.io/bluepy-doc/scanentry.html
        # DREAM only wants adtype = 0xff (0d255) for manufacturer data
        # values is a list where the last element is the manufacturer data
        values = [value for (adtype, desc, value) in triples if adtype == 255]
        if len(values):
            packet = {
                "tag_id": tag_id,
                "rssi": rssi,
                "timestamp": int(time.time()),
                "mfr_data": values[-1]
            }
    except (UnicodeEncodeError, UnicodeDecodeError):
        # If there's a unicode error, disregard it since it isn't a Fujitsu Tag
        print("Discarding on Unicode error (non Fujitsu)")
        return None
    return packet