#!/usr/bin/env python
# Copyright 2018 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import argparse
import json
import logging
import os
import requests
import sys
import time

from google.auth import crypt, jwt
import google.auth.transport.requests

def run(args):
  audience = '{project}.appspot.com'.format(
    project=args.project_id)
  key_path = args.service_account_path
  with open(os.path.expanduser(key_path), mode='rt') as f:
    service_account_json = json.load(f)
  email = service_account_json['client_email']
  creds = jwt.Credentials.from_service_account_file(key_path, audience=audience,
                                                    additional_claims={
                                                        'email': email
                                                    })
  session = google.auth.transport.requests.AuthorizedSession(creds)
  response = session.post(
      'https://{project}.appspot.com/_ah/api/greeting/v1/greet'.format(
          project=args.project_id))
  logging.info("Service JSON response: %s", json.dumps(response.json(), indent=2))


def main(args):
  logging.basicConfig(
      level=logging.DEBUG,
      format='%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s',
  )
  run(args)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Make a call to the Greetings API using a service account.')
  parser.add_argument('service_account_path', type=str, help='The path to your service account file.')
  parser.add_argument('project_id', type=str, help='The project ID of the server whose API you want to call.')

  parsed_args = parser.parse_args()
  main(parsed_args)
