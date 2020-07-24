# Using Endpoints on Google Compute Engine or Container Engine

This repository contains samples and utilities for using Google Cloud Endpoints on GCE(Google Compute Engine) or GKE(Google Kubernetes Engine)

## Repository Structure:
* [gettting-started](gettting-started): ESPv2 Google Kubernetes Engine deployment yaml files used in Cloud Endpoint [tutorials](https://cloud.google.com/endpoints/docs/openapi/tutorials).
* [gke](gke): ESPv2 deployment yaml files for Google Kubernetes Engine.
* [kubernetes](kubernetes): ESPv2 deployment yaml files for Kubernetes. It is almost the same as GKE except that they all need to mount a service account key file to the ESP container.
* [k8s](k8s): ESPv1 deployment files for mixed GKE(Google Kubernetes Engine) and Kubernetes deployment. If a file is has `_gke` in the file name it is for GKE, otherwise it is for Kubernetes.
