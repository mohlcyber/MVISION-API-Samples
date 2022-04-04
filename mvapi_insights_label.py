# Written by mohlcyber - 04.04.2022
# Script to pull Campaings with a specific label

import requests
import json
import logging

from argparse import ArgumentParser, RawTextHelpFormatter

logger = logging.getLogger('logs')
logger.setLevel('DEBUG')
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class MVAPI():
    def __init__(self):
        self.base_url = 'https://api.mvision.mcafee.com'
        self.session = requests.Session()

        # MVAPI Keys
        api_key = ''
        client_id = ''
        client_token = ''

        self.headers = {
            'x-api-key': api_key,
            'Content-Type': 'application/vnd.api+json'
        }

        auth = (client_id, client_token)

        self.auth(auth)

    def auth(self, auth):
        iam_url = "https://iam.mcafee-cloud.com/iam/v1.1/token"

        payload = {
            "grant_type": "client_credentials",
            "scope": "ins.user"
        }

        res = self.session.post(iam_url, headers=self.headers, auth=auth, data=payload)
        if res.ok:
            access_token = res.json()['access_token']
            self.headers['Authorization'] = 'Bearer ' + access_token
            self.session.headers.update(self.headers)
            logger.info('Successfull authenticated.')
        else:
            logger.error('Error in mvapi.auth. HTTP: {0} - {1}'.format(res.status_code, res.text))
            exit()

    def get_campaigns(self, category):
        count = 0
        filters = {
            'fields': 'id,name,threat_level_id,coverage,is_coat,description,kb_article_link,external_analysis,'
                      'created_on,prevalence,is_profile,threat_profile_type,related_campaigns,categories',
            'limit': 2000
        }

        res = self.session.get(self.base_url + '/insights/v2/campaigns', params=filters)
        if res.ok:
            for campaign in res.json()['data']:
                if category in campaign['attributes']['categories']:
                    logger.info(json.dumps(campaign))
                    count += 1

            logger.info('Found {0} campaigns with the label {1}'.format(count, category))
        else:
            logger.error('Error in mvapi.get_campaigns. HTTP: {0} - {1}'.format(res.status_code, res.text))
            exit()

    def main(self):
        self.get_campaigns(args.label)


if __name__ == '__main__':
    usage = """python mvapi_insights_label.py -L <LABEL>"""
    title = 'MVISION API - MVISION Insights search for label'
    parser = ArgumentParser(description=title, usage=usage, formatter_class=RawTextHelpFormatter)

    parser.add_argument('--label', '-L',
                        required=True, type=str,
                        help='MVISION Insights Label')

    args = parser.parse_args()

    MVAPI().main()
