import requests
import json

from utils import current_time_millis


class Ecobici(object):
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base = "https://pubsbapi.smartbike.com"
        self.token_object = None
        self.expiration_time = None

    def stations_list(self):
        url = "{}/api/v1/stations.json?access_token={}".format(self.base, self.get_access_token())
        r = requests.get(url)
        return r.json()

    def stations_status(self):
        url = "{}/api/v1/stations/status.json?access_token={}".format(self.base, self.get_access_token())
        r = requests.get(url)
        return r.json()


    def get_access_token(self):
        if self.token_object is None:
            self.token_object = self.get_token()
            self.expiration_time = current_time_millis() + int(self.token_object['expires_in']) * 1000
        elif self.expiration_time < current_time_millis():
            self.token_object = self.refresh_token()
            self.expiration_time = current_time_millis() + int(self.token_object['expires_in']) * 1000

        return self.token_object['access_token']

    def get_token(self):
        url = "{}/oauth/v2/token?client_id={}&client_secret={}&grant_type=client_credentials".format(self.base, self.client_id, self.client_secret)
        r = requests.get(url)
        return r.json()

    def refresh_token(self):
        url = "{}/oauth/v2/token?client_id={}&client_secret={}&grant_type=refresh_token&refresh_token={}".format(self.base, self.client_id, self.client_secret, self.token_object['refresh_token'])
        r = requests.get(url)
        return r.json()



def find_by_id(station_id, status_list):
    for e in status_list['stationsStatus']:
        if e['id'] == station_id:
            return e

    return None


def check_events(stations_list, s1, s2):
    events_list = []
    stations_ids = [e['id'] for e in stations_list['stations']] 
    for st_id in stations_ids:
        e1 = find_by_id(st_id, s1)
        e2 = find_by_id(st_id, s2)
        if (not e1 is None) and (not e2 is None):
            bikes_diff = e1['availability']['bikes'] - e2['availability']['bikes']
            slots_diff = e1['availability']['slots'] - e2['availability']['slots']
            if bikes_diff != 0 or slots_diff != 0:
                evt = {'station_id': st_id, 'timestamp': current_time_millis(), 'bike_diff':bikes_diff, 'slot_diff': slots_diff}
                events_list.append(evt)

    return events_list
