"""
Cloud Function: Background Function

For details, visit:
https://cloud.google.com/functions/docs/writing/background#functions_background_parameters-python
"""

import base64
import json

from google.cloud import bigquery


client = bigquery.Client()
dataset_id = 'dream_assets_raw_packets'
table_id = 'measurements_table'
table_ref = client.dataset(dataset_id).table(table_id)
table = client.get_table(table_ref)

# Run under Python 3.7 runtime
def run(data, context):

    print("data published: ", data)

    # data['data'] is somehow base64 encoded 
    payload = base64.b64decode(data['data']).decode('utf-8')
    row = json.loads(payload)
    tag_id  = row['tag_id']
    mfr_data = row['mfr_data']

    rows = [
            (tag_id, mfr_data)
    ]

    errors = client.insert_rows(table, rows)
    assert errors == []