from __future__ import absolute_import, unicode_literals
from celery import shared_task
import os
import socket
import time
import json
from dreamhub import dreamconfig
from google.oauth2 import service_account
import googleapiclient.discovery
import base64

# During setup, we set the RasPi's hostname to the Hub ID  
HUB_ID = socket.gethostname()
SCOPES = ['https://www.googleapis.com/auth/pubsub']
# The Hub publishes to this topic on PubSub 
TOPIC = "projects/{}/topics/{}".format(dreamconfig.GOOGLE_PROJECT_ID, dreamconfig.GOOGLE_PUBSUB_TOPIC)
SERVICE_ACCOUNT_FILE = dreamconfig.GOOGLE_APPLICATION_CREDENTIALS
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

#@app.task(base=Batches,flush_every=100, flush_interval=60)
@shared_task(name="publisher.publish", rate_limit=1, timeout=5)
def publish(payload):
    # @TODO clean up encoding!
    try:
        enc = base64.b64encode(json.dumps(payload).encode('utf-8'))
    except Exception as e:
        print("Couldn't encode payload (type: %s, error: %s)" % (type(payload),e))
        raise
    message = {
        "messages": [
            {
                "data": enc,
                "attributes": {
                    "hub_id": HUB_ID,
                    "hub_publisher_version": dreamconfig.VERSION,
                    "hub_timestamp": time.time()
                }
            }
        ]
    }
    try:
        pubsub = googleapiclient.discovery.build('pubsub', 'v1', credentials=credentials)
        res = pubsub.projects().topics().publish(topic=TOPIC, body=message).execute()
        return res
    except Exception as e:
        print("Unable to publish data to Google Cloud due to network error: {}".format(e))
        raise

