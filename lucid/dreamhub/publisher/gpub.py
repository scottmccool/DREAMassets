import socket
import time
import json
import base64
import os

from dreamhub import dreamconfig

from google.cloud import pubsub_v1

# During setup, we set the RasPi's hostname to the Hub ID  
HUB_ID = socket.gethostname()

# This replaces sobun publish method and conforms better to google cloud api docs
# We send the observation as a utf-8 encoded string and set attributes as appropriate
# @todo add batching logic
def publish_message(msg, msg_type, topic=dreamconfig.GOOGLE_PUBSUB_TOPIC):
    try:
        msg = json.dumps(msg).encode('utf-8')
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(dreamconfig.GOOGLE_PROJECT_ID, topic)
        publisher.publish(topic_path,
            data=msg,
            hub_id=HUB_ID,
            hub_publisher_version=dreamconfig.VERSION,
            hub_timestamp = str(time.time()),
            type = "observation"
        )
    except Exception as e:
        print("Unable to publish message to Google Cloud due to error: {}".format(e))
        raise
