export VCAP_SERVICES='{
  "user-provided": [
   {
    "credentials": {
     "client_id": "oohimtelling",
     "client_secret": "oohimtelling",
     "uri": "https://uaa.10.244.0.34.xip.io/oauth/token?grant_type=client_credentials"
    },
    "label": "user-provided",
    "name": "uaa",
    "syslog_drain_url": "",
    "tags": []
   },
   {
    "credentials": {
     "uri": "https://api.10.244.0.34.xip.io"
    },
    "label": "user-provided",
    "name": "cloud_controller",
    "syslog_drain_url": "",
    "tags": []
   }
  ]
 }'