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

GOOGLE_ID_AUDIENCE = "https://www.googleapis.com/oauth2/v4/token"

def make_signed_jwt(service_account_key_path, audience, subject=None, ttl_seconds=3600, **kwargs):
  """Generate a JWT token signed by a Google Cloud Platform service account.

  Args:
    service_account_key_path: (str) A full path to a Google Cloud Platform
      service account file (in JSON format) to use to sign the JWT.
    audience: (str) The recipients that the JWT is intended for.

  Keyword arguments:
    subject: (str) An optional claim that identifies the subject of the JWT.
    ttl_seconds: (int) The time, in seconds, after which the JWT will not
      be accepted.
    **kwargs: Any additional keyword arguments are encoded as JSON in the
      payload of the JWT.
  """
  with open(os.path.expanduser(service_account_key_path), mode='rt') as f:
      service_account_info = json.load(f)

  signer = crypt.RSASigner.from_service_account_info(service_account_info)

  now = int(time.time())
  if subject is None:
    subject = service_account_info['client_email']
  payload = {
      'iat': now,
      'exp': now + ttl_seconds,
      'sub': subject,
      'iss': service_account_info['client_email'],
      'email': service_account_info['client_email'],
      'aud': audience,
  }
  payload.update(**kwargs)
  logging.debug("JWT payload: %r", payload)
  signed_jwt = jwt.encode(signer, payload)
  logging.debug("Signed JWT: %s", signed_jwt)

  return signed_jwt


def make_google_id_token(service_account_key_path, audience, **kwargs):
  signed_jwt = make_signed_jwt(
      service_account_key_path=service_account_key_path,
      audience=GOOGLE_ID_AUDIENCE,
      target_audience=audience,
  )

  # send the JWT to Google Token endpoints to request Google ID token

  params = {
      'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
      'assertion': signed_jwt
  }
  headers = {"Content-Type": "application/x-www-form-urlencoded"}
  response = requests.post('https://www.googleapis.com/oauth2/v4/token', data=params, headers=headers)
  res = response.json()

  logging.debug("JSON response: %s", json.dumps(res, indent=2))

  google_id_token = res['id_token']
  logging.debug('Google ID token: %s', google_id_token)

  claims = jwt.decode(google_id_token, verify=False)
  logging.info("Google ID token claims: %s", json.dumps(claims, indent=2))
  return google_id_token


def run(args):
  audience = '{project}.appspot.com'.format(
    project=args.project_id)
  key_path = args.service_account_path
  if args.use_google_id_token:
     bearer = make_google_id_token(
       service_account_key_path=key_path,
       audience=audience,
   )
  else:
    bearer = make_signed_jwt(
      service_account_key_path=key_path,
      audience=audience,
    )

  headers = {'Authorization': 'Bearer {}'.format(bearer)}
  response = requests.post(
      'https://{project}.appspot.com/_ah/api/greeting/v1/greet'.format(
        project=args.project_id),
      headers=headers,
      verify=True,
  )
  response.raise_for_status()
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
  parser.add_argument('--use_google_id_token', action='store_true',
    help='If true, will use a Google ID token for authentication, rather than a service account.')

  parsed_args = parser.parse_args()
  main(parsed_args)
