# written by mohlcyber v.0.0.1 - 01.11.2021
# Script to assign and unassign tags to system in MVISION EPO

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
        self.tag = args.tag
        self.type = args.type

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
            "scope": "epo.tags.w epo.device.r epo.tags.r epo.device.w"
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

    def get_ids(self, type, query):
        param = {
            'filter[name][eq]': query
        }

        res = self.session.get(self.base_url + '/epo/v2/{0}'.format(type), params=param)

        if res.ok:
            if len(res.json()['data']) == 0:
                self.logger.error(
                    'Could not find {0} in MVISION EPO. \n {1} - {2}'.format(type, res.status_code, res.text))
                sys.exit()
            elif len(res.json()['data']) > 1:
                self.logger.error(
                    'Identified more than one {0} in MVISION EPO.\n {1} - {2}'.format(
                        type, res.status_code, res.text))
                sys.exit()
            else:
                id = res.json()['data'][0]['id']
                self.logger.info('Identified {0} in MVISION EPO. {0}ID for {1} is {2}.'.format(type[:-1], query, id))

                return id
        else:
            self.logger.error('Error in get_ids. {0} - {1}'.format(res.status_code, res.text))
            sys.exit()

    def assign_tag(self, did, tid):
        payload = {
          "data": [
            {
              "type": "tags",
              "id": int(tid)
            }
          ]
        }

        if self.type == 'assign':
            res = self.session.post(self.base_url + '/epo/v2/devices/{0}/relationships/assignedTags'.format(did),
                                      data=json.dumps(payload))
        else:
            res = self.session.delete(self.base_url + '/epo/v2/devices/{0}/relationships/assignedTags'.format(did),
                                      data=json.dumps(payload))

        if res.ok:
            self.logger.info('Successfully {0} Tag {1} to System {2}.'.format(self.type + 'ed', self.tag, self.host))
        else:
            if res.status_code == 409:
                self.logger.error('Conflict - Tag already {0} to system. {1} - {2}'.format(self.type, res.status_code, res.text))
            if res.status_code == 404:
                self.logger.error('Conflict - Tag already {0} from system. {1} - {2}'.format(self.type, res.status_code, res.text))
            else:
                self.logger.error('Conflict: Error in assign_tag. {0} - {1}.'.format(res.status_code, res.text))

    def main(self):
        did = self.get_ids('devices', self.host)
        tid = self.get_ids('tags', self.tag)

        self.assign_tag(did, tid)


if __name__ == '__main__':
    usage = """python mvapi_epo_assign_tag.py -H <HOSTNAME> -T <TAG NAME> -A <TYPE>"""
    title = 'MVISION API - EPO Tag Assignment'
    parser = ArgumentParser(description=title, usage=usage, formatter_class=RawTextHelpFormatter)

    parser.add_argument('--host', '-H',
                        required=True, type=str,
                        help='Hostname')

    parser.add_argument('--tag', '-T',
                        required=True, type=str,
                        help='MVISION EPO Tag Name')

    parser.add_argument('--type', '-A',
                        required=True, type=str,
                        choices=['assign', 'unassign'],
                        help='Should tag be assigned or unassigned?')

    args = parser.parse_args()
    MVAPI().main()
