# Cloud Endpoints JavaScript client using Google ID Token

Please see `makeEndpointsRequest()` in `index.html`
for how to make a request to an API managed by Google Cloud Endpoints.

## Setting up the OAuth client ID

* Go to https://console.cloud.google.com
* Select an existing project. You can also create a project in [Google Developer
  Console](https://console.developers.google.com/project). The project
  you select can be the same as your backend project or a separate one.
* Navigate to Credentials page and create an OAuth client ID for web
  application. Add the URL to the `index.html` on your web server to the Authorized
  Javascript origins. You will use this client ID in the next step.
* Replace the content of google-signin-client_id in index.html with the client
  ID that was created in the previous step.

## Deploy your backend

Edit the OpenAPI document for your API, typically `openapi.yaml`, and make sure 
the API surface, or a specific methods, are configured to accept Google ID Tokens.

In particular, your OpenAPI document might include a security definition entry that
looks like the following:

    google_id_token:
      authorizationUrl: ""
      flow: "implicit"
      type: "oauth2"
      x-google-issuer: "https://accounts.google.com"
      x-google-jwks_uri: "https://www.googleapis.com/oauth2/v3/certs"
      # Your OAuth2 client's Client ID must be added here.
      # You can add multiple client IDs to accept tokens form multiple clients.
      x-google-audiences: "YOUR-CLIENT-ID"

And individual methods can be labeled with the following security annotation:

    security:
    - google_id_token: []

If your API is hosted on a different domain than the enclosing page,
please make sure your backend handles
[CORS](https://en.wikipedia.org/wiki/Cross-origin_resource_sharing).

Deploy the backend. Instructions may vary depending on what programming language
you are using. For example, with Node.js Bookstore example backend, update
`host` property in the Swagger spec file, and run the `gcloud deploy` command:

    gcloud --project=YOUR_PROJECT_ID beta app deploy

## Running

Below is an example of the app after a successful request.

![an example of the app after a successful request](screenshot.png)


## Additional information

Additional information about Google Sign-In for web is available at
https://developers.google.com/identity/sign-in/web.
