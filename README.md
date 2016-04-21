Oooh I'm Telling
================

Report on all the apps that are running in CF, their build packs  and when they got there.

In order to tell on everyone you need a client with cloud_controller.admin authority. Otherwise you'll only be able to see the apps that are scoped to your identity, which is either none, or whoever you are in Cloud Foundry.

#Add a client
```
uaac target uaa.local.pcfdev.io --skip-ssl-validation
uaac token client get admin -s admin-client-secret
uaac client add oohimtelling --scope uaa.none --authorized_grant_types "client_credentials"  --authorities "cloud_controller.admin cloud_controller.read" --redirect_uri http://example.com
```

Your admin client secret is in your cf manifest, if using pcfdev check [this](https://github.com/pivotal-cf/pcfdev/blob/62dfcabd3cce6dd9e2f82995e444ae99c9fa3e95/images/manifest.yml#L348)

#Present UAA & CloudController to the APP

In an untested theory you can give your client_id a grant other than client_credentials, but I've only tested this and the code assumes that the UAA URI will return
json which contains an `access_token` that it will then insert as a `bearer` token in future requests to the CF CLI. It also assumes uaa provides an `expires_in` field that it will use to grab a new token.

`cf cups uaa -p '{ "uri": "http://uaa.local.pcfdev.io/oauth/token?grant_type=client_credentials", "client_id": "oohimtelling", "client_secret": "oohimtelling" }'`

`cf cups cloud_controller -p '{ "uri": "https://api.local.pcfdev.io" }'`

#Auth
The app uses http basic auth. Reuse the client_id and client_secret when challenged for creds.

#SSL Validation
If you see this in your logs you most likely have an SSL issue:

`SSLError: [Errno 1] _ssl.c:507: error:14090086:SSL routines:SSL3_GET_SERVER_CERTIFICATE:certificate verify failed`

Setting the environment variable `VERIFY_SSL` to `false` will cause the application
to skip ssl verification. This is handy with bosh-lite / pcfdev installs or installs where
the application does not know about the root ca of your environment.

#Security Groups
Make sure the security group applied to your space allows the app to access uaa
and the cloud controller.

#Test it locally
source `env.sh` into your environment to get `VCAP_SERVICES` set locally. It assumes you're using pcfdev and have created the client as I have above.

```
$ python app.py
```
Browse to `localhost:8003/apps`

Should yield you some json that looks something like this

```
{
  "apps": [
    [
      {
        "app_guid": "0d658ce1-0cf3-403a-aa89-f88c5c0ce09d",
        "buildpack": null,
        "created_at": "2015-07-07T16:12:45Z",
        "name": "investigator",
        "org": "jdk-org",
        "routes": [
          "investigator.10.244.0.34.xip.io"
        ],
        "space": "jdk-space",
        "updated_at": "2015-07-07T16:12:52Z"
      }
    ],
    [
      {
        "app_guid": "af9ecd72-6f74-4d03-9c9f-2c8895808d11",
        "buildpack": "PHP",
        "created_at": "2015-07-09T16:38:20Z",
        "name": "ph",
        "org": "jdk-org",
        "routes": [
          "ph.10.244.0.34.xip.io"
        ],
        "space": "jdk-space",
        "updated_at": "2015-07-09T16:38:36Z"
      }
    ],
    [
      {
        "app_guid": "d99911ff-115d-4fa8-9ac7-0d529d6b96ad",
        "buildpack": "Python",
        "created_at": "2015-07-17T21:39:58Z",
        "name": "oohimtelling",
        "org": "test-org",
        "routes": [
          "oohimtelling-pettish-phenetole.10.244.0.34.xip.io"
        ],
        "space": "test-space",
        "updated_at": "2015-07-17T21:57:13Z"
      }
    ]
  ]
}
```

#Push it to CF
Make sure you didn't skip the `cups` step above, that would be a disaster.

`cf push`

Browse to <cf-url>/apps

#TODO
* Maybe an html page at the root
