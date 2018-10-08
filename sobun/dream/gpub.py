# This file sends data from the RasPi to Google PubSub
#
# The dataflow in DREAM is bleAdvertisement -> packet -> payload
# At this point in the project, DREAM sends *payloads* via PubSub to BigQuery

from __future__ import print_function

import json
import socket

from google.cloud import pubsub
from google.cloud.pubsub import types

# During setup, we set the RasPi's hostname to the Hub ID in DREAM
HUB_ID = socket.gethostname()

# Let's revisit batch size during optimization
# TODO move max_messages to config file 
topic = "projects/dream-assets-project/topics/tags-dev"
publisher = pubsub.PublisherClient(
    batch_settings=types.BatchSettings(max_messages=50), )

# reduce the packet to a payload and send it to BigQuery via PubSub
# syncer.py calls this function 
def send_data(packet):
    payload = clean(packet)
    future = publisher.publish(topic, payload)
    print("sending payload: ", payload)
    msg_id = future.result()
    if not msg_id:
        # TODO make celery retry
        # raise "Something went wrong. Try again"
        pass

# TODO make clean a private function; only used by send_data 
def clean(packet):
    # NOTE payload must be bytestring

    # We add metadata here so we don't have change the schema of the "queue" packet for celery
    # It's faster to tack on hub ID here, rather than when pushing into the queue 
    packet['hub_id'] = HUB_ID

    # Fujitsu's mfr_data value has measurements in the last 16 characters (8 bytes)
    mfr_data = packet.pop('mfr_data')
    measurements = mfr_data[-16:]
    packet['measurements'] = measurements

    payload = json.dumps(packet)
    return payload


# the code below will only be run if we invoke it from the command line: python -m dream.gpub
# this block of code allows us to test gpub from our laptop, without a RasPi 
if __name__ == "__main__":
    from time import time 
    tag_id = 1
    while True:
        tag_id += 1
        packet = {
            "hub_id": HUB_ID,
            "tag_id": tag_id,
            "rssi": 2,
            "measurements": "foobarhexcode",
            "timestamp": time(),
        }
        send_data(packet)
