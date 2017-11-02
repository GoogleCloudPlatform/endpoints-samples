# Endpoints DNS with SSL certificate issued by Let's Encrypt through Kube-Lego

This example demonstrates how to deploy an Endpoints service on GKE with automatic
provisioning of an SSL certificate for the .cloud.goog service domain.

## Requirements

For this example, you need:

 -  A proper installation of the Cloud SDK, configured with an account and a project:
    ```bash
    gcloud config list
    # [core]
    # account = ...
    # project = ...
    ```
    Make sure your gcloud installation is up-to-date:
    ```bash
    gcloud components update
    ```
    Make sure your credentials are up-to-date:
    ```bash
    gcloud auth login
    ```
- A proper GKE cluster created in your project:
    ```bash
    CLUSTER_NAME=endpoints-dns-sample
    CLUSTER_ZONE="us-west1-a"
    gcloud services enable container.googleapis.com
    gcloud container clusters create ${CLUSTER_NAME} --zone=${CLUSTER_ZONE} --num-nodes=3
    gcloud container clusters get-credentials ${CLUSTER_NAME} --zone=${CLUSTER_ZONE}
    ```
    Notes: Creating a new GKE cluster may take several minutes.

## Deployment

You can deploy the example either by running the `deploy.sh` script, or by running through
the detailed steps described below manually.
The `deploy.sh` script confirms your account email address and your GCP project ID,
then automatically runs through the detailed steps in sequence.

### Detailed steps

1. Configure and deploy KubeLego

    - Edit `lego/1-configmap.yaml` and make sure your email address is set.
      This is important to receive expiration notifications from Let's Encrypt
      before your certificates expire.

      ```bash
      EMAIL="..."
      sed -i "s/\[YOUR_EMAIL_ADDRESS_HERE\]/${EMAIL}/g" lego/1-configmap.yaml
      ```

    - Deploy KubeLego:

      ```bash
      kubectl apply -f lego/
      # namespace "kube-lego" created
      # configmap "kube-lego" created
      # deployment "kube-lego" created
      ```

2. Configure your Project ID:

    ```bash
    PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
    sed -i "s/\[PROJECT_ID\]/${PROJECT_ID}/g" echo/*.yaml
    ```

3. Create the service Ingress

    ```bash
    kubectl apply -f echo/0-namespace.yaml -f echo/1-ingress.yaml
    # namespace "echo" created
    # ingress "echo-ingress" created
    ```

4. Wait for the Ingress controller to assign a public IP address and configure Endpoints DNS accordingly

    ```bash
    kubectl get --namespace=echo ingress echo-ingress
    # NAME           HOSTS                                     ADDRESS   PORTS     AGE
    # echo-ingress   echo.endpoints.taton-codelab.cloud.goog             80, 443   33s

    # Later...

    kubectl get --namespace=echo ingress echo-ingress
    # NAME           HOSTS                                     ADDRESS          PORTS     AGE
    # echo-ingress   echo.endpoints.taton-codelab.cloud.goog   130.211.14.157   80, 443   33s
    ```

    Note: it make take up to a minute for a public IP to be assigned.

    ```bash
    INGRESS_IP_ADDRESS="$(kubectl get --namespace=echo ingress echo-ingress \
        -o jsonpath='{.status.loadBalancer.ingress[0].ip}')"
    sed -i "s/\[INGRESS_IP_ADDRESS\]/${INGRESS_IP_ADDRESS}/g" echo/*.yaml
    ```

5. Deploy the OpenAPI specification

    ```bash
    gcloud endpoints services deploy echo/openapi.yaml
    # ...
    # Service Configuration [2017-11-01r0] uploaded for service [echo.endpoints.[PROJECT_ID].cloud.goog]
    ```

6. Configure the backend with the service config ID

    ```bash
    CONFIG_ID=$(gcloud endpoints configs list \
        --service=echo.endpoints.${PROJECT_ID}.cloud.goog --limit=1 --format="value(id)")
    sed -i "s/\[CONFIG_ID\]/${CONFIG_ID}/g" echo/*.yaml
    ```

7. Deploy the backend

    ```bash
    kubectl apply -f echo/2-service.yaml -f echo/3-deployment.yaml
    # service "echo-service" created
    # deployment "echo-backend" created
    ```

8.  Wait for Kube-Lego to provision an SSL/TLS certificates

    It may take in the order of 15 minutes for all the systems and configurations to converge.
    Eventually, the Ingress controller will be configured with a TLS certificate provisioned by Let's Encrypt.


## Verify the service deployment

In order to verify the correct operation of the Endpoints service, you will need a valid API
key for your project, which you can create by navigating to:
https://console.cloud.google.com/apis/credentials

You can then send the following request to the Endpoints service as follows:
```bash
API_KEY="..."    # fill in your API key here
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
curl --request POST \
    --header "Content-Type: application/json" \
    --data '{"message":"hello"}' \
    "https://echo.endpoints.${PROJECT_ID}.cloud.goog/echo?key=${API_KEY}"
# {
#   "message": "hello"
# }
```

If the certificate has not been provisioned and deployed yet, the `curl` command above
will fail with the following error:
```
curl: (35) Unknown SSL protocol error in connection to echo.endpoints.[PROJECT_ID].cloud.goog:443
```

### Verify the certificate details

You can verify the content of the certificate with the following command:

```bash
openssl s_client -connect echo.endpoints.${PROJECT_ID}.cloud.goog:443 < /dev/null
# CONNECTED(00000003)
# depth=1 C = US, O = Let's Encrypt, CN = Let's Encrypt Authority X3
# verify error:num=20:unable to get local issuer certificate
# verify return:0
# ---
# Certificate chain
#  0 s:/CN=echo.endpoints.$PROJECT_ID.cloud.goog
#    i:/C=US/O=Let's Encrypt/CN=Let's Encrypt Authority X3
#  1 s:/C=US/O=Let's Encrypt/CN=Let's Encrypt Authority X3
#    i:/O=Digital Signature Trust Co./CN=DST Root CA X3
# ...
```

## Cleanup

Delete the `echo` and the `kube-lego` namespaces:

```bash
kubectl delete namespace echo kube-lego
# namespace "echo" deleted
# namespace "kube-lego" deleted
```

If you had created a dedicated GKE cluster for the example, you can delete it:

```bash
gcloud container clusters delete ${CLUSTER_NAME} --zone=${CLUSTER_ZONE}
```

## Troubleshooting

### Is the DNS entry for the service correctly configured?

Make sure the DNS entry for the service has been correctly configured to the IP address of the Ingress:
```bash
dig echo.endpoints.${PROJECT_ID}.cloud.goog
# ;; ANSWER SECTION:
# echo.endpoints.$PROJECT_ID.cloud.goog. 59 IN A $INGRESS_IP_ADDRESS
```

### Does the Kube-Lego self test work?

```bash
curl http://echo.endpoints.${PROJECT_ID}.cloud.goog/.well-known/acme-challenge/_selftest
# xQWxEVkEGhCuiifC
```

### Does the TLS secret exist and contain a certificate?

```bash
kubectl --namespace=echo get secret echo-tls
# NAME       TYPE                DATA      AGE
# echo-tls   kubernetes.io/tls   2         5m
```
