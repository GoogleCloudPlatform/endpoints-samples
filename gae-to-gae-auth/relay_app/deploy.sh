#!/usr/bin/env bash
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


set -o nounset
set -o errexit

if [[ "$#" != "2" ]]; then
  echo "Usage: ./deploy <greeting-project-name> <relay-project-name>"
  exit 1
else
  BACKEND_PROJECT_ID="$1"
  PROJECT_ID="$2"
  SERVICE="${PROJECT_ID}.appspot.com"
fi

if [[ ! -f py27-venv/bin/activate ]]; then
  virtualenv -p python2.7 py27-venv
fi

# Temporarily disable nounset, because virtualenv relies on having it disabled.
set +u
source py27-venv/bin/activate
set -u

rm -rf lib
pip install --requirement requirements.txt --target lib

sed -r \
  -e "s#YOUR-PROJECT-ID#${PROJECT_ID}#g" \
  -e "s#GREETINGS-PROJECT-ID#${BACKEND_PROJECT_ID}#g" \
  main.py.template > main.py

# Generate OpenAPI spec from Python application code:
# The OpenAPI spec is written to `relayv1openapi.json`.
python lib/endpoints/endpointscfg.py get_openapi_spec \
  --hostname="${SERVICE}" \
  main.RelayApi

# Deploy the OpenAPI spec:
gcloud --project "$PROJECT_ID" endpoints services deploy relayv1openapi.json

CONFIG_VERSION=$(gcloud --project "$PROJECT_ID" endpoints configs list \
  --service="$SERVICE" \
  --sort-by="~config_id" --limit=1 --format="value(CONFIG_ID)" \
  | tr -d '[:space:]')

sed \
  -e "s#\${SERVICE}#${SERVICE}#g" \
  -e "s#\${CONFIG_VERSION}#${CONFIG_VERSION}#g" \
  -e "s#\${BACKEND}#${BACKEND_PROJECT_ID}#g" \
  app.yaml.template > app.yaml

gcloud --project "$PROJECT_ID" app create --region us-east4 || true
gcloud --project "$PROJECT_ID" app deploy $PWD --quiet
