# Google Cloud Endpoints on GKE - Echo Example

## Step 1: Prepare and deploy your service's Swagger API specification.

    Open the swagger.yaml file and in the host property, replace MY_PROJECT_ID
    with the ID of the Google Cloud Platform project where you'd like to deploy
    the sample application.

    gcloud alpha service-management deploy swagger.yaml

    This command will output a service name and a service version value which
    you will need to provide in the esp_echo_*.yaml files below.

    But first, enable the API service which you deployed above on your
    own project:

    gcloud alpha service-management enable \
      --consumer-project=MY_PROJECT_ID \
      --service=MY_PROJECT_ID.appspot.com

## Step 2: Install kubectl and provide your service name and service version

    gcloud components update kubectl

## Step 3: Deploy your service on GKE

Bring up a single service running ESP+echo with one of the following
options. For each sample below, edit the .yaml file and replace SERVICE_NAME and
SERVICE_VERSION with the values from Step 1 above.

For testing purpose, you can generate self-signed nginx.key and nginx.cert using openssl:
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ./nginx.key -out ./nginx.crt

  * Start esp+echo serving http requests only

        kubectl create -f esp_echo_http.yaml

  * Start esp+echo serving http/https requests

        kubectl create secret generic nginx-ssl \
          --from-file=./nginx.crt --from-file=./nginx.key

        kubectl create -f esp_echo.yaml

  * Start esp+echo serving http/https requests with custom nginx.conf

        kubectl create secret generic nginx-ssl \
            --from-file=./nginx.crt --from-file=./nginx.key

        kubectl create configmap nginx-config --from-file=nginx.conf

        kubectl create -f esp_echo_custom_config.yaml

## References

  * [echo sample code](https://github.com/GoogleCloudPlatform/python-docs-samples/tree/master/appengine/flexible/endpoints)
    (swagger.yaml in this directory is a copy from this echo sample)

  * [echo docker image](https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/appengine/flexible/endpoints/Dockerfile.container-engine)
