1. Create appropriate projects to deploy backends and ESP.
2. Enable [Cloud Firestore in Datastore mode](https://cloud.google.com/firestore/docs/firestore-or-datastore#in_datastore_mode) for your backend project.
3. Deploy app engine app to App Engine Standard.
4. Enable IAP for App Engine Standard with ESP project's default service account (e.g. `esp-project-id@appspot.gserviceaccount.com`) as "IAP-secured Web App User"; copy down the OAuth2 Client Id for IAP.
5. Deploy cloud function to Cloud Functions.
6. Enable ESP project's default service account as "Cloud Functions Invoker" on the cloud function.
7. Deploy ESP: `gcloud alpha run deploy vehicles-esp --region us-central1 --image gcr.io/endpoints-jenkins/endpoints-runtime-serverless:debian-git-571d3c96b1911191d062b6644a205fcfda02f083`
8. Copy hostname of ESP project into swagger spec, replacing "CLOUD RUN APP HOSTNAME"
9. Copy app engine app address into swagger spec, replacing "APP ENGINE ADDRESS"
10. Copy IAP OAuth2 Client Id into swagger spec, replacing "IAP OAUTH2 CLIENT ID"
11. Copy cloud function address into swagger spec, replacing "CLOUD FUNCTION ADDRESS"
12. Deploy swagger spec: `gcloud endpoints services deploy swagger.json`
13. Set service name in ESP env variables: `gcloud alpha run configurations update --region us-central1 --service vehicles-esp --set-env-vars="^|^SERVICE_NAME=CLOUD RUN APP HOSTNAME"`
