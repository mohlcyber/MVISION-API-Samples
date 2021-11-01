# written by mohlcyber v.0.0.1 - 01.11.2021
# Script to get system details from MVISION EPO

import sys
import requests
import json
import logging

from argparse import ArgumentParser, RawTextHelpFormatter


class MVAPI():
    def __init__(self):
        self.base_url = 'https://api.mvision.mcafee.com'
        self.session = requests.Session()

        self.host = args.host

        self.api_key = ''
        client_id = ''
        client_token = ''

        auth = (client_id, client_token)

        self.logging()
        self.auth(auth)

    def logging(self):
        self.logger = logging.getLogger('logs')
        self.logger.setLevel('DEBUG')
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def auth(self, auth):
        iam_url = "https://iam.mcafee-cloud.com/iam/v1.1/token"

        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/vnd.api+json'
        }

        payload = {
            "grant_type": "client_credentials",
            "scope": "epo.device.r"
        }

        res = self.session.post(iam_url, headers=headers, auth=auth, data=payload)

        if res.status_code != 200:
            self.logger.error("Could not authenticate to get the IAM token: {0} - {1}".format(res.status_code, res.text))
            sys.exit()
        else:
            self.logger.info('Successful authenticated.')
            access_token = res.json()['access_token']
            headers['Authorization'] = 'Bearer ' + access_token
            self.session.headers = headers

    def get_device(self):
        param = {
            'filter[name][eq]': self.host
        }

        res = self.session.get(self.base_url + '/epo/v2/devices'.format(type), params=param)

        if res.ok:
            if len(res.json()['data']) == 0:
                self.logger.error('Could not find system with the hostname {0} in MVISION EPO.'.format(self.host))
            else:
                self.logger.info(json.dumps(res.json(), indent=2))
        else:
            self.logger.error('Error in get_ids. {0} - {1}'.format(res.status_code, res.text))
            sys.exit()

    def main(self):
        self.get_device()


if __name__ == '__main__':
    usage = """python mvapi_epo_get_devices.py -H <HOSTNAME>"""
    title = 'MVISION API - EPO Get Devices'
    parser = ArgumentParser(description=title, usage=usage, formatter_class=RawTextHelpFormatter)

    parser.add_argument('--host', '-H',
                        required=True, type=str,
                        help='Hostname')

    args = parser.parse_args()
    MVAPI().main()
