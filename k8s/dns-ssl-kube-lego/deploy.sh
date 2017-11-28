#!/usr/bin/env bash

set -o errexit
set -o nounset

# Step 1
EMAIL="$(gcloud config get-value account 2>/dev/null)"
read -e -p "Enter your email address (for Let's Encrypt to send certificate expiration notifications): " -i $EMAIL EMAIL
sed -i "s/\[YOUR_EMAIL_ADDRESS_HERE\]/$EMAIL/g" lego/1-configmap.yaml

# Step 2
echo "Deploying KubeLego in the kube-lego namespace"
kubectl apply -f lego/

# Step 3
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
read -e -p "Enter the project ID: " -i $PROJECT_ID PROJECT_ID
sed -i "s/\[PROJECT_ID\]/$PROJECT_ID/g" echo/*.yaml

# Step 4
echo "Deploying Kubernetes Ingress"
kubectl apply -f echo/0-namespace.yaml -f echo/1-ingress.yaml

# Step 5
echo "Waiting for Ingress public IP address..."
while true; do
	kubectl get --namespace=echo ingress echo-ingress
	INGRESS_IP_ADDRESS="$(kubectl get --namespace=echo ingress echo-ingress \
			        -o jsonpath='{.status.loadBalancer.ingress[0].ip}')"
	if [[ -z "$INGRESS_IP_ADDRESS" ]]; then
		sleep 5
	else
		break
	fi
done

echo "Ingress IP address : $INGRESS_IP_ADDRESS"
sed -i "s/\[INGRESS_IP_ADDRESS\]/$INGRESS_IP_ADDRESS/g" echo/*.yaml

# Step 6
echo "Deploying Endpoints service configuration"
gcloud endpoints services deploy echo/openapi.yaml

# Step 7
CONFIG_ID=$(gcloud endpoints configs list \
		--service=echo.endpoints.$PROJECT_ID.cloud.goog --limit=1 --format="value(id)")
sed -i "s/\[CONFIG_ID\]/$CONFIG_ID/g" echo/*.yaml

# Step 8
echo "Deploying the echo backend"
kubectl apply -f echo/2-service.yaml -f echo/3-deployment.yaml

# Step 9
echo "In a few minutes, https://echo.endpoints.$PROJECT_ID.cloud.goog should be provisioned with a Let's Encrypt certificate"
