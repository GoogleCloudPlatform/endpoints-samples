# Run ESP (Extensible Service Proxy) on Kubernetes

The Extensible Service Proxy, a.k.a. ESP, is an [NGINX](http://nginx.org)-based proxy
that sits in front of your backend code. It processes incoming traffic to
provide auth, API Key management, logging, and other Endpoints
API Management features.

This document describes how to run ESP (packaged as a docker image
`gcr.io/endpoints-release/endpoints-runtime:1`) with
[Google Cloud Endpoints](https://cloud.google.com/endpoints/) integration on a
Kubernetes cluster that can run anywhere as long as it has internet access.

## Prerequisites

* [Set up a Kubernetes Cluster](http://kubernetes.io/docs/getting-started-guides/)
* [Installing `kubectl`](http://kubernetes.io/docs/user-guide/prereqs/)

## Before you begin

1. Select or create a [Cloud Platform Console project](https://console.cloud.google.com/project).

2. [Enable billing](https://support.google.com/cloud/answer/6293499#enable-billing) for your project.

3. Note the project ID, because you'll need it later.

4. Install [cURL](https://curl.haxx.se/download.html) for testing purposes.

5. [Enable Cloud Endpoints API](https://console.cloud.google.com/apis/api/endpoints.googleapis.com/overview)
   for your project in the Google Cloud Endpoints page in the API Manager.
   Ignore any prompt to create credentials.

6. [Download the Google Cloud SDK](https://cloud.google.com/sdk/docs/quickstarts).

## Configuring Endpoints

To configure Endpoints, replace `YOUR-PROJECT-ID` with your own project ID in
the [openapi.yaml](openapi.yaml) configuration file:
    
   ```
   swagger: "2.0"
   info:
     description: "A simple Google Cloud Endpoints API example."
     title: "Endpoints Example"
     version: "1.0.0"
   host: host: "echo-api.endpoints.YOUR-PROJECT-ID.cloud.goog"
   ```

## Deploying the sample API config to Google Service Management

To deploy the sample application:

1. Invoke the following command:

   ```
   gcloud service-management deploy openapi.yaml
   ```

   The command returns several lines of information, including a line similar to the following:

   ```
   Service Configuration [2017-02-13-r2] uploaded for service [echo-api.endpoints.example-project.cloud.goog]
   ```

   Note that the configuration ID that is displayed will change when you deploy a new version of the API.

2. Make a note of the service name and the service configuration ID because you'll need
them later when you configure the container cluster for the API.

## Deploying the sample API to the cluster

To deploy to the cluster:

1. Edit the Kubernetes configuration file,
i.e. [esp_echo_http.yaml](esp_echo_http.yaml),
replacing `SERVICE_NAME` and `SERVICE_CONFIG_ID` shown in the snippet below with
the values returned when you deployed the API:

   ```
   containers:
     - name: esp
       image: gcr.io/endpoints-release/endpoints-runtime:1
       args: [
         "-p", "8080",            # the port ESP listens on
         "-a", "127.0.0.1:8081",  # the backend address
         "-s", "SERVICE_NAME",
         "-v", "SERVICE_CONFIG_ID",
         "-k", "/etc/nginx/creds/service-account-creds.json",  # not needed for GKE
       ]
   ```

   Note you also need to change the service type from LoadBalancer to NodePort
   if you use [MiniKube](http://kubernetes.io/docs/getting-started-guides/minikube/)

2. (Not necessary if your kubernetes cluster is on [GKE](https://cloud.google.com/container-engine/))
   Create your service account credentials


  * Download your credential as `service-account-creds.json` from
    [Google API Console](https://cloud.google.com/storage/docs/authentication#generating-a-private-key). Make sure you selected the following roles when creating your service account key (Note you need to scroll down the role selection menu to find the second and third roles):
    
    * Project -> Viewer
    * Cloud Trace -> Cloud Trace Agent
    * Service Management -> Service Controller


  * Deploy the service account credentials to the cluster.

   ```
   kubectl create secret generic service-account-creds --from-file=service-account-creds.json
   ```

3. Start the service using the kubectl create command:

   ```
   kubectl create -f esp_echo_http.yaml
   ```

   or use `esp_echo_http_gke.yaml` on GKE

   ```
   kubectl create -f esp_echo_http_gke.yaml
   ```

## (Optional) Add SSL support

Have your SSL key and certificate ready as `nginx.key` and `nginx.crt`.
For testing purpose, you can generate self-signed `nginx.key` and `nginx.cert`
using openssl.  

   ```
   # For testing purpose only
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
       -keyout ./nginx.key -out ./nginx.crt

   # Create the k8s secret from your prepared nginx creds
   kubectl create secret generic nginx-ssl \
       --from-file=./nginx.crt --from-file=./nginx.key

   # Use GKE deployment as the example here
   kubectl create -f esp_echo_gke.yaml
   ```

## (Optional) Use your custom `nginx.conf`

   ```
   # Create the k8s secret from your prepared nginx creds
   kubectl create secret generic nginx-ssl \
       --from-file=./nginx.crt --from-file=./nginx.key

   # Create the k8s configmap from your prepared nginx.conf
   kubectl create configmap nginx-config --from-file=nginx.conf

   # Use GKE deployment as the example here
   kubectl create -f esp_echo_custom_config_gke.yaml
   ```

## Get the service's external IP address (skip this step if you use Minikube)

It can take a few minutes after you start your service in the container before
the external IP address is ready.

To view the service's external IP address:

1. Invoke the command:

   ```
   kubectl get service
   ```

2. Note the value for EXTERNAL-IP; you'll need it to send requests to the API.

## Sending a request to the sample API

After the sample API is running in the container cluster, you can send requests
to the API.

To send a request to the API

1. [Create an API key](https://console.cloud.google.com/apis/credentials)
   in the API credentials page.

  * Click Create credentials, then select API key > Server key, then click
    Create.

  * Copy the key, then paste it into the following export statement:

    ```
    export ENDPOINTS_KEY=AIza...
    ```

2. Send an HTTP request using curl, as follows,

  * If you don't use Minikube:

    ```
    curl -d '{"message":"hello world"}' -H "content-type:application/json" http://[EXTERNAL-IP]/echo?key=${ENDPOINTS_KEY}
    ```

  * Otherwise:

    ```
    NODE_PORT=`kubectl get service esp-echo --output='jsonpath={.spec.ports[0].nodePort}'`

    MINIKUBE_IP=`minikube ip`

    curl -d '{"message":"hello world"}' -H "content-type:application/json" ${MINIKUBE_IP}:${NODE_PORT}/echo?key=${ENDPOINTS_KEY}
    ```

## Using GCE L7 Load Balancer with ESP

[GLBC](https://github.com/kubernetes/contrib/tree/master/ingress/controllers/gce) is a Kubernetes ingress controller
that configures external loadbalancers. We can use GLBC to route traffic from an external IP address to an ESP-enabled
Kubernetes service. By default, [Google Container Engine](https://cloud.google.com/container-engine/) deploys GLBC as a
cluster addon. If you do not use Google Container Engine, then you need to
[install GLBC](https://github.com/kubernetes/contrib/tree/master/ingress/controllers/gce) in your cluster.

To use GLBC with ESP, we need to create an ingress resource in addition to a service and a deployment.
Edit the file `esp_echo_gke_ingress.yaml` and replace service name and config version with your values.
Notice that we use `-z` flag and a `readinessProbe` to define a health-checking endpoint on the application
port. Deploy these resources to your cluster:


  ```
  kubectl create -f esp_echo_gke_ingress.yaml
  ```

You can check the status of your ingress using the following command:

  ```
  kubectl describe ingress
  ```

Once you obtain an external address, we can send a request to the echo backend:

  ```
  curl -d '{"message":"hello world"}' -H "content-type:application/json" http://${INGRESS_IP_ADDRESS}/echo?key=${ENDPOINTS_KEY}
  ```

If you do not see a response from ESP immediately, please wait for a couple of minutes and retry.

## References

  * [echo sample code](https://github.com/GoogleCloudPlatform/python-docs-samples/tree/master/appengine/flexible/endpoints)

  * [echo docker image](https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/appengine/flexible/endpoints/Dockerfile.container-engine)
