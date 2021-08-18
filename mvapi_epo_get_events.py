#!/usr/bin/env python3
# Written by mohlcyber v.0.0.1 (18.08.2021)
# Script to retrieve threat events from MVISION EPO via MVISION API

import os
import sys
import logging
import requests
import json

from datetime import datetime, timedelta
from argparse import ArgumentParser, RawTextHelpFormatter


class MVAPI():
    def __init__(self):
        self.base_url = 'https://api.mvision.mcafee.com'
        self.session = requests.Session()

        # MVAPI Keys
        self.api_key = ''
        client_id = ''
        client_token = ''

        auth = (client_id, client_token)

        self.cache_fname = os.path.dirname(os.path.abspath(__file__)) + '/cache.log'
        if os.path.isfile(self.cache_fname):
            cache = open(self.cache_fname, 'r')
            self.pull_time = cache.read()
            cache.close()
        else:
            self.pull_time = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

        self.logging()
        self.auth(auth)

    def logging(self):
        self.logger = logging.getLogger('logs')
        self.logger.setLevel('INFO')
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def auth(self, auth):
        try:
            iam_url = "https://iam.mcafee-cloud.com/iam/v1.1/token"

            headers = {
                'x-api-key': self.api_key,
                'Content-Type': 'application/vnd.api+json'
            }

            payload = {
                "grant_type": "client_credentials",
                "scope": "epo.evt.r"
            }

            res = self.session.post(iam_url, headers=headers, auth=auth, data=payload)

            if res.ok:
                access_token = res.json()['access_token']
                headers['Authorization'] = 'Bearer ' + access_token
                self.session.headers = headers
                self.logger.debug('Debug epo.auth() - {0} - {1}'.format(res.status_code, res.text))

            if res.status_code != 200:
                self.logger.error('Error in epo.auth(). Error: {} - {}'.format(str(res.status_code), res.text))
                sys.exit()

        except Exception as error:
            self.logger.error('Error in epo.auth(). Error: {}'.format(str(error)))
            sys.exit()

    def get_events(self):
        try:
            params = {
                'filter[timestamp][GT]': self.pull_time,
                'sort': '-timestamp',
                'page[limit]': 1000
            }

            nextItem = None
            nextFlag = True
            mvepo_events_dict = []
            cacheFlag = False

            while (nextFlag):
                if nextItem:
                    url = self.base_url + nextItem
                    res = self.session.get(url)
                else:
                    url = self.base_url + '/epo/v2/events'
                    res = self.session.get(url, params=params)

                if res.ok:
                    self.logger.debug('Debug epo.get_events() - {0} - {1}'.format(res.status_code, res.text))
                    res = res.json()
                    if len(res['data']) > 0:
                        if cacheFlag is False:
                            cache = open(self.cache_fname, 'w')
                            cache.write(res['data'][0]['attributes']['timestamp'])
                            cache.close()
                            cacheFlag = True

                        for event in res['data']:
                            mvepo_event = event['attributes']
                            mvepo_event['id'] = event['id']
                            mvepo_event['type'] = event['type']
                            mvepo_event['url'] = event['links']['self']

                            mvepo_events_dict.append(dict(mvepo_event))

                        if res and res.get("links") and res.get("links").get("next"):
                            nextItem = res["links"]["next"]
                            nextFlag = True
                        else:
                            nextFlag = False

                    else:
                        self.logger.debug('No new MVISION EPO Events identified. Exiting. {0}'.format(json.dumps(res)))
                        sys.exit()

                else:
                    self.logger.error('Error in epo.get_events(). Error: {0} - {1}'.format(str(res.status_code), res.text))
                    sys.exit()

            for event in mvepo_events_dict:
                self.logger.info(json.dumps(event))
            return mvepo_events_dict

        except Exception as error:
            self.logger.error('Error in epo.get_events(). Error: {}'.format(str(error)))
            sys.exit()


if __name__ == '__main__':
    usage = """python mvapi_epo_get_events.py"""
    title = 'MVISION API - MVISION EPO Events'
    parser = ArgumentParser(description=title, usage=usage, formatter_class=RawTextHelpFormatter)

    args = parser.parse_args()

    MVAPI().get_events()
