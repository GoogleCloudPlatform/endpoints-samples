# Using Endpoints on Google Compute Engine or Container Engine

This repository contains samples and utilities for using Google Cloud Endpoints v2 on Compute Engine or Container Engine

Folder structures:
* gettting-started: ESPv2 GKE depolyment yaml files used Cloud Endpoint [tutorials](https://cloud.google.com/endpoints/docs/openapi/tutorials).
* gke: ESPv2 deployment yaml files for GKE.
* kubernetes: ESPv2 deployment yaml files for k8s. They all need to mount a service account key file.
* k8s: The mixed GKE and k8s deployment files for legacy ESPv1. If a file is for GKE, it has `_gke` in the file name.
