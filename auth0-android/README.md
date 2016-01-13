# Auth0 + Android + API Seed

This is the seed project you need to use if you're going to create an app that will use Auth0, Android and an API that you're going to be developing. That API can be in any language.

## Configuring the example

You must set your Auht0 `ClientId` and `Domain` in this sample so that it works. For that, just open the `app/src/main/res/values/auth0.xml` file and replace the `{CLIENT_ID}` and `{DOMAIN}` fields with your account information.
Also replace `{MOBILE_CUSTOM_SCHEME}` with your ClientId in lowercase with `a0` prefix, e.g.: `a0YOUR_CLIENT_ID`

## Running the example

From the command line run the following commands inside the sample folder

```bash
./gradlew installDebug
adb shell am start -n com.auth0.sample/.MainActivity 
```

Enjoy your Android app now :).
