# Copyright 2016 Google Inc. All Rights Reserved.
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
from jinja2 import Environment, PackageLoader


def main(properties):
    env = Environment(loader=PackageLoader('templates'), trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('esp_template.jinja')

    out_path = properties['out']
    del properties['out']

    with open(out_path, 'w') as out_file:
        out_file.write(template.render(properties=properties))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate a Kubernetes config for your Endpoints API')

    # Required
    parser.add_argument(
        '--service-name',
        help='The hostname of your service. Usually \"my-project-id.appspot.com\".',
        required=True
    )
    parser.add_argument(
        '--service-version',
        help='The generation id of your service. Run gcloud alpha service-management service describe <service-name> and look for the \"generation\" field',
        required=True
    )
    parser.add_argument(
        '--api-image',
        required=True,
        help='The docker image that serves your API traffic'
    )
    # Optional
    parser.add_argument(
        '--out',
        default='esp_config.yaml',
        help='Output path for your config'
    )
    parser.add_argument(
        '--proxy-port',
        default=8080,
        type=int,
        help='The port on which traffic will be served by the endpoints server proxy'
    )
    parser.add_argument(
        '--ssl',
        type=bool,
        default=False,
        help='Whether to use SSL termination. If true you must have a secret in your cluster named \"nginx-ssl\" which provides certs and secrets'
    )
    parser.add_argument(
        '--ssl-port',
        type=int,
        default=443,
        help='If --ssl is False has no effect. Customizes the port the nginx proxy serves SSL traffic on'
    )
    parser.add_argument(
        '--api-port',
        type=int,
        default=8081,
        help='The port that nginx proxies to, and your API image to serve traffic on'
    )
    parser.add_argument(
        '--custom-nginx-config',
        type=bool,
        default=False,
        help='Whether or not you provide a custom configuration for the nginx proxy. If true you must havea configmap in your cluster named \"nginx-config\"'
    )
    parser.add_argument(
        '--replicas',
        type=int,
        default=1,
        help='Number of replicas or your API container to maintain in the cluster.'
    )
    parsed = parser.parse_args()
    main(vars(parsed))
