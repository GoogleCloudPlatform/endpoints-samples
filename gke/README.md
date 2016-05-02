# Google Cloud Endpoints on GKE - Bookstore Example

## Step 1: Prepare and deploy your service's Swagger API specification.

    Open the swagger.json file and in the host property, replace MY_PROJECT_ID
    with the ID of the Google Cloud Platform project where you'd like to deploy
    the sample application.

    gcloud alpha service-management deploy ../swagger.json

    This command will output a service name and a service version value which
    you will need to provide in the esp_bookstore_*.yaml files below.

    But first, enable the API service which you deployed above on your
    own project:

    gcloud alpha service-management enable \
      --consumer-project=MY_PROJECT_ID \
      --service=MY_PROJECT_ID.appspot.com

## Step 2: Install kubectl and provide your service name and service version

    gcloud components update kubectl

## Step 3: Deploy your service on GKE

Bring up a single service running ESP+Bookstore with one of the following
options. Note that the bookstore container image is created from
`../Dockerfile`. For each sample, edit the .yaml file and replace
SERVICE_NAME and SERVICE_VERSION with the values from Step 1 above.

  * Start esp+bookstore serving http requests only

        kubectl create -f esp_bookstore_http.yaml

  * Start esp+bookstore serving http/https requests

        kubectl create secret generic nginx-ssl \
          --from-file=./nginx.crt --from-file=./nginx.key

        kubectl create -f esp_bookstore.yaml

  * Start esp+bookstore serving http/https requests with custom nginx.conf

        kubectl create secret generic nginx-ssl \
            --from-file=./nginx.crt --from-file=./nginx.key

        kubectl create configmap nginx-config --from-file=nginx.conf

        kubectl create -f esp_bookstore_custom_config.yaml
