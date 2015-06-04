Oooh I'm Telling
================

Report on all the apps that are running in CF, their build packs  and when they got there. 

In order to tell on everyone you need a client with cloud_controller.admin authority. Otherwise you'll only be able to see the apps that are scoped to your identity, which is either none, or whoever you are in Cloud Foundry. 

#Add a client
```
uaac client add oohimtelling --scope uaa.none --authorized_grant_types "authorization_code, client_credentials, refresh_token"  --authorities "cloud_controller.admin cloud_controller.read" --redirect_uri http://example.com
```

#Present UAA & CloudController to the APP

In an untested theory you can give your client_id a grant other than client_credentials, but I've only tested this and the code assumes that the UAA URI will return 
json which contains an `access_token` that it will then insert as a `bearer` token in future requests to the CF CLI. It also assumes uaa provides an `expires_in` field that it will use to grab a new token.

`cf cups uaa -p '{ "uri": "https://uaa.10.244.0.34.xip.io/oauth/token?grant_type=client_credentials", "client_id": "oohimtelling", "client_secret": "oohimtelling" }'`

`cf cups cloud_controller -p '{ "uri": "https://api.10.244.0.34.xip.io" }'`

#Test it locally
source `env.sh` into your environment to get `VCAP_SERVICES` set locally. It assumes you're using bosh-lite and have created the client as I have above. 

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
        "buildpack": "Node.js",
        "created_at": "2015-05-23T23:04:00Z",
        "name": "node_v1.0",
        "org": "test-org",
        "routes": [
          "node.10.244.0.34.xip.io",
          "node-prod.10.244.0.34.xip.io"
        ],
        "space": "test-space",
        "updated_at": "2015-05-29T05:43:14Z"
      }
    ],
    [
      {
        "buildpack": "Node.js",
        "created_at": "2015-05-24T00:34:20Z",
        "name": "node_v1.1",
        "org": "test-org",
        "routes": [
          "node2.10.244.0.34.xip.io",
          "node-prod.10.244.0.34.xip.io"
        ],
        "space": "test-space",
        "updated_at": "2015-05-29T05:43:14Z"
      }
    ],
    [
      {
        "buildpack": "PHP",
        "created_at": "2015-06-04T04:16:59Z",
        "name": "php",
        "org": "jdk-org",
        "routes": [
          "php-odontophorous-shovelhead.10.244.0.34.xip.io"
        ],
        "space": "jdk-space",
        "updated_at": "2015-06-04T04:17:19Z"
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
* Maybe an html page at the route
* Make skipping ssl validation an option
* Basic auth with the client secret maybe... 