# written by mohlcyber v.0.0.1 - 09.08.2021
# Script to add new MVISION EPO tags

import sys
import requests
import json
import logging

from argparse import ArgumentParser, RawTextHelpFormatter
from datetime import datetime


class MVISIONAPI():
    def __init__(self):
        self.base_url = 'https://api.mvision.mcafee.com'
        self.session = requests.Session()

        self.api_key = ''
        client_id = ''
        client_token = ''

        auth = (client_id, client_token)

        self.logging()
        self.auth(auth)

        self.tagname = args.tag
        self.taggroup = args.group

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
            "scope": "epo.taggroup.r epo.tags.w"
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

    def get_tag_groups(self):
        res = self.session.get(self.base_url + '/epo/v2/tagGroups')

        if res.ok:
            if len(res.json()['data']) > 1 and self.taggroup is None:
                self.logger.error('Multiple Tag Groups identified. Please provide a Tag Group to create new tags.')
                sys.exit()

            check = 0
            for group in res.json()['data']:
                check += 1
                if group['attributes']['groupName'] == self.taggroup:
                    self.logger.info('Successful identified corresponding Tag Group. Group Id: {0}'
                                     .format(group['id']))
                    return group['id']

                if check == len(res.json()['data']):
                    self.logger.error('Could not find corresponding Tag Group.')
                    sys.exit()

        else:
            self.logger.error('Error in get_tag_groups. HTTP {0} - {1}'.format(str(res.status_code), res.text))
            sys.exit()

    def create_tag(self, taggroup_id):
        now = datetime.astimezone(datetime.now())
        tz = str(now).split('.')[1][-6:]
        dtime = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + tz

        payload = {
            "data": {
                "type": "tags",
                "attributes": {
                    "uniqueKey": "",
                    "name": self.tagname,
                    "family": "EPO",
                    "notes": "Default tag for systems identified as a Server",
                    "criteria": "( where ( eq EPOComputerProperties.OSPlatform \"Server\" ) )",
                    "whereClause": "where ( [EPOComputerProperties].[OSPlatform] = 'Server' )",
                    "executeOnAsci": "true",
                    "createdBy": "mvapi",
                    "createdOn": dtime,
                    "modifiedBy": "mvapi",
                    "modifiedOn": dtime,
                    "tagGroupId": int(taggroup_id)
                }
            }
        }

        res = self.session.post(self.base_url + '/epo/v2/tags', data=json.dumps(payload))
        if res.ok:
            self.logger.info('Tag {0} successfully created'.format(self.tagname))
        elif res.status_code == 409:
            self.logger.error('Tag already exist.')
            sys.exit()
        else:
            self.logger.error('Could not create tag. HTTP {0} - {1}'.format(str(res.status_code), res.text))
            sys.exit()

    def main(self):
        taggroup_id = self.get_tag_groups()
        self.create_tag(taggroup_id)


if __name__ == '__main__':
    usage = """python mvapi_epo_add_tag.py -T <TAG NAME> -G <TAG GROUP>"""
    title = 'MVISION API - EPO Tag Assignment'
    parser = ArgumentParser(description=title, usage=usage, formatter_class=RawTextHelpFormatter)

    parser.add_argument('--tag', '-T',
                        required=True, type=str,
                        help='MVISION EPO Tag Name')

    parser.add_argument('--group', '-G',
                        required=False, type=str,
                        default=None, help='MVISION EPO Tag Group')

    args = parser.parse_args()

    MVISIONAPI().main()
