import os
GOOGLE_PROJECT_ID = os.environ.get("GOOGLE_PROJECT_ID", "creyon-mccool-dev")
GOOGLE_PUBSUB_TOPIC = os.environ.get("GOOGLE_PUBSUB_TOPIC ", "dream-log")
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "/usr/local/sobun/config/hub-dream-log-publisher.json")
BLE_SCANTIME = os.environ.get("BLE_SCANTIME","5")
VERSION = "0.0.1"