# Written by mohlcyber - 18.08.2021
# Sample script to search hashes in MVISION Insights via MVISION API

import sys
import requests
import logging

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
            "scope": "ins.user ins.suser ins.ms.r"
        }

        res = self.session.post(iam_url, headers=headers, auth=auth, data=payload)

        if res.status_code != 200:
            self.logger.error('Could not authenticate to get the IAM token: {0} - {1}'.format(res.status_code, res.text))
            sys.exit()
        else:
            self.logger.info('Successful authenticated.')
            access_token = res.json()['access_token']
            headers['Authorization'] = 'Bearer ' + access_token
            self.session.headers = headers

    def search_ioc(self):
        filters = {
            'filter[type][eq]': 'md5',
            'filter[value]': args.hash,
            'fields': 'id, type, value, coverage, uid, is_coat, is_sdb_dirty, category, comment, campaigns, threat, prevalence',
            'limit': 1
        }
        res = self.session.get(self.base_url + '/insights/v2/iocs', params=filters)

        if res.ok:
            if len(res.json()['data']) == 0:
                self.logger.info('No Hash details in MVISION Insights found.')
            else:
                self.logger.info(res.text)
        else:
            self.logger.error('Error in search_ioc. HTTP {0} - {1}'.format(str(res.status_code), res.text))
            sys.exit()

    def main(self):
        self.search_ioc()


if __name__ == '__main__':
    usage = """python mvapi_insights_search.py -H <MD5 Hash>"""
    title = 'MVISION API - MVISION Insights Search for Hash'
    parser = ArgumentParser(description=title, usage=usage, formatter_class=RawTextHelpFormatter)

    parser.add_argument('--hash', '-H',
                        required=True, type=str,
                        help='MD5 Hash to search for')

    args = parser.parse_args()
    MVAPI().main()
