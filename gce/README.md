# Deploying Endpoints APIs on Google Compute Engine

This repository provides a template and instructions for setting up an API scalably on Google Compute Engine using Managed Instance Groups, Load Balancers, and Autoscalers. For a single instance setup walkthrough check out the [Endpoints Compute Engine doc](https://cloud.google.com/endpoints/docs/gce)

## Using GCE Startup Scripts


## Using Deployment Manager Templates

[globally_available_service.py](./globally_available_service.py) is a Google Cloud Deployment Manager Template. If you are not already familiar with Deployment Manager check out [the docs](https://cloud.google.com/deployment-manager/docs/). To use this template with your own API follow the directions below:

### Step 1: Prepare and deploy your service's Swagger API specification.

    gcloud alpha service-management deploy swagger.json

    This command will output a service name and a service version value which
    you will need to provide in your Deployment Manager config.

    But first, enable the API service which you deployed above on your
    own project:

    gcloud alpha service-management enable \
      --consumer-project=MY_PROJECT_ID \
      --service=MY_PROJECT_ID.appspot.com

### Step 2: Upload a startup script and (optionally) a nginx config.

This repository provides an example [startup.sh](./startup.sh) script that installs the Endpoints Server PRoxy (ESP) directly on your GCE instance. This particular startup script installs the example API provided in [python-docs-samples](https://github.com/GoogleCloudPlatform/python-docs-samples/tree/master/managed_vms/endpoints). However, by replacing the code between the comments you can repurpose this script for your own API. After you have done this, upload it to a cloud storage bucket in your project, and note the path.

If you want to customize the configuration of the ESP, you can also upload an `nginx.conf` file to the Cloud Storage

## Step 3: Write your configuration file.

For an example of a configuration you can see the [example config](./config.yaml). For a full accounting of options check out the [template schema](./globally_available_service.py.schema).

In particular, make sure to replace the values under `metadata:` with your own values from Step 1 and 2. Note, the only supported OS at this time is Debian-Jessie.

## Step 4: Deploy your configuration

Run `gcloud deployment-manager deployments create [DEPLOYMENT_NAME] --config config.yaml` to deploy your configuration.
