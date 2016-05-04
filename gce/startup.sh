#!/bin/bash

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

NGINX_CONF_URL=$(curl -f http://metadata/computeMetadata/v1/instance/attributes/nginx-conf-url -H "METADATA-FLAVOR: Google")

# Create an environment variable for the correct distribution
export CLOUD_ENDPOINTS_REPO="google-cloud-endpoints-$(lsb_release -c -s)"

# Add the Cloud SDK distribution URI as a package source
echo "deb http://packages.cloud.google.com/apt $CLOUD_ENDPOINTS_REPO main" | sudo tee /etc/apt/sources.list.d/google-cloud-endpoints.list

# Import the Google Cloud public key
curl --silent https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -

# Update and install the Cloud SDK
sudo apt-get update
sudo apt-get install -y endpoints-runtime

if [ $NGINX_CONF_URL ]; then
    gsutil cp $NGINX_CONF_URL /etc/nginx/nginx.conf
fi

# Use restart in case there is a custom config
sudo /usr/sbin/service nginx restart

### START YOUR SERVICE HERE ###

sudo apt-get install -y  build-essential libssl-dev libffi-dev python-dev git python-pip gunicorn

git clone https://github.com/GoogleCloudPlatform/python-docs-samples

cd python-docs-samples/managed_vms/endpoints
virtualenv env
source env/bin/activate
pip install -r requirements.txt

# 8081 is the default port to which the ESP proxies
sudo gunicorn -b :8081 --access-logfile /var/log/service.log main:app &
###
