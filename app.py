#!/usr/bin/env python
from __future__ import print_function
import json 
import requests 
import sys
import os
from flask import Flask
from flask import jsonify

Flask.get = lambda self, path: self.route(path, methods=['get'])

#token = os.environ['CF_ACCESS_TOKEN']
client_id='oohimtelling'
client_secret='oohimtelling'
uaa_url='https://uaa.10.244.0.34.xip.io/oauth/token?grant_type=client_credentials'
api = "https://api.10.244.0.34.xip.io"
cache = dict() 
port = 8003

if 'PORT' in os.environ:
    port = int(os.getenv("PORT"))
    
def get_token():
    client_auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
    r = requests.get(url=uaa_url, headers={'accept': 'application/json'},
        params={'grant_type': 'client_credentials'}, auth=client_auth, verify=False)
    return r.json()
    
def cf(path):
    token = get_token()
    access_token="bearer " + token['access_token']
    hdr = {'Authorization': access_token}
    r = requests.get(api + path, headers=hdr, verify=False)
    if r.status_code != 200: 
        print("Failed to call CF API (" + path + ")", file=sys.stderr)
    return r.json()
    
def api_cache(url):
    if url not in cache: 
        cache[url] = cf(url)
    return cache[url]

def get_apps():
    apps = []
    for app in cf('/v2/apps')['resources']:
        a = dict()
        a['name'] = app['entity']['name']
        a['created_at'] = app['metadata']['created_at']
        a['updated_at'] = app['metadata']['updated_at']
        buildpack = app['entity']['buildpack']
        detected_buildpack = app['entity']['detected_buildpack']
        if buildpack is None: 
            buildpack = detected_buildpack
        a['buildpack'] = buildpack
        space = api_cache(app['entity']['space_url'])
        a['space'] = space['entity']['name']
        org = api_cache(space['entity']['organization_url'])
        a['org'] = org['entity']['name']
        routes = cf(app['entity']['routes_url'])
        a['routes'] = []
        for route in routes['resources']:
            host = route['entity']['host']
            domain = api_cache(route['entity']['domain_url'])['entity']['name']
            a['routes'].append(host + "." + domain)
        apps.append([a])
        
    return apps
    
app = Flask(__name__)

@app.get('/apps')
def get_root():
    return jsonify(apps=get_apps())
                
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port, debug=True)