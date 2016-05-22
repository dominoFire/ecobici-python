import json
import requests

from utils import current_time_millis


def post_event_flume(url, object):
    data_object = [{
        'headers': {
            'timestamp': current_time_millis()
        },
        'body': json.dumps(object)
    }]

    requests.post(url, json=data_object)

    return data_object
