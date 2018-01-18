# App Engine-to-App Engine Authentication

### Note: This is not an official Google product.

## Before you begin


### Requirements

- [Python 2.7.*](https://www.python.org/downloads/)
- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [Curl](https://curl.haxx.se/download.html)
- Bash (Windows users, see [this
  guide](https://docs.microsoft.com/en-us/windows/wsl/install-win10) for
  installing Bash on Windows)

For this example, you'll need to create two GCP projects.

One project will host a simple "greeting" that says
"Hello, username@account.com". The other project will host an API that
acts as a "relay".

Make sure to [enable billing](https://console.cloud.google.com/billing/)
for both projects before continuing.

## Instructions


### Preparation

1. Export variable names for each of your projects.
Change `YOUR-GREETING-PROJECT-NAME` and `YOUR-RELAY-PROJECT-NAME` to the respective
project names of your two projects (note: it doesn't matter which project you
use for each task as long as you keep them consistent).
```
export GREETING=YOUR-GREETING-PROJECT-NAME
export RELAY=YOUR-RELAY-PROJECT-NAME
```
2. Clone this repository.
```
git clone https://github.com/GoogleCloudPlatform/endpoints-samples
```
3. Change directories to `gae-to-gae-auth`.
```
cd gae-to-gae-auth
```

### Deploying the Greeting API

1. Deploy your greeting application.
```
cd greeting_app
./deploy.sh "$GREETING" "$RELAY"
```

2. Send an unauthenticated request to your application.
```
curl \
    --request POST \
    --data "" \
    "https://${GREETING}.appspot.com/_ah/api/greeting/v1/greet"
```
You should see an error like this:
```
{
"error": {
  "code": 401,
  "errors": [
  {
    "domain": "global",
    "message": "Missing or invalid token",
    "reason": "required"
  }
  ],
  "message": "Missing or invalid token"
}
}
```
The greeting API expects a valid user credential to be sent along with each
request. In the next step, you'll use a service account and a Python client
to send an authenticated request to the greeting API.


### Using the client

1. Create a service account
([Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts))
under your greeting project with the name *my-service-account*. Save the
service account credentials as JSON under the `./client` directory.

2. Change directories to the client.
```
cd ../client
```

3. Setup your client and virtualenv.
```
./setup.sh
source py27-venv/bin/activate
```

4. Use the client to send an authenticated request to your greeting server.
Replace `YOUR_SERVICE_ACCOUNT_FILE` with the name of the service account JSON
credentials you downloaded previously.
```
./client.py YOUR_SERVICE_ACCOUNT_FILE "$GREETING"
```
You should see a message that looks like:
```
2001-11-21 13:51:17,198 INFO client.py:91 Service JSON response: {
  "message": "Hello, my-service-account@your-project-name.iam.gserviceaccount.com"
}
```

5. Deactivate the virtualenv used for the client.
```
deactivate
```


### Using the Relay

1. Change directories to the relay application.
```
cd ../relay_app
```

2. Deploy the relay.
```
./deploy.sh "$GREETING" "$RELAY"
```

3. Send an unauthenticated request to the relay.
```
curl "https://${RELAY}.appspot.com/_ah/api/relay/v1/relay"
```
You should see a message that greets the service account of the relay app:
```
{
 "content": "{\n \"message\": \"Hello, relay-app@appspot.gserviceaccount.com\"\n}"
}
```

For every request to the relay, it forwards that
request, plus authentication headers, to the greeting API. It then returns
the result of the greeting API to the original requester.
Congratulations! You've successfully deployed a cross-App Engine
authentication solution. 
