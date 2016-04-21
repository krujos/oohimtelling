export VCAP_SERVICES='{
  "user-provided": [
   {
    "credentials": {
     "client_id": "oohimtelling",
     "client_secret": "oohimtelling",
     "uri": "http://uaa.local.pcfdev.io/oauth/token?grant_type=client_credentials"
    },
    "label": "user-provided",
    "name": "uaa",
    "syslog_drain_url": "",
    "tags": []
   },
   {
    "credentials": {
     "uri": "https://api.local.pcfdev.io"
    },
    "label": "user-provided",
    "name": "cloud_controller",
    "syslog_drain_url": "",
    "tags": []
   }
  ]
 }'
