import os
GOOGLE_PROJECT_ID = os.environ.get("GOOGLE_PROJECT_ID", "dream-assets-project")
GOOGLE_PUBSUB_TOPIC = os.environ.get("GOOGLE_PUBSUB_TOPIC ", "batched-payloads")
BATCH_SIZE = os.environ.get("CLOUD_BATCH_SIZE", "10")
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "/usr/local/dream/sobun/config/google-credentials.secret.json")
BTLE_TIMEOUT = os.environ.get("BTLE_TIMEOUT","20.0")