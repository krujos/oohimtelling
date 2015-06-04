#!/usr/bin/env python
#Script runs as whoever is logged into the CF API. 
from __future__ import print_function
import json 
import requests 
import sys
import os
from flask import Flask

Flask.get = lambda self, path: self.route(path, methods=['get'])

token = os.environ['CF_ACCESS_TOKEN']
headers = {'Authorization': token}
api = "https://api.10.244.0.34.xip.io"
cache = dict() 

port = 8003
if 'PORT' in os.environ:
    port = int(os.getenv("PORT"))
    
def cf(path):
    r = requests.get(api + path, headers=headers, verify=False)
    if r.status_code != 200: 
        print("Failed to call CF API (" + path + ")", file=sys.stderr)
        sys.exit(1)
    return r.json()
    
def api_cache(url):
    if url not in cache: 
        cache[url] = cf(url)
    return cache[url]


app = Flask(__name__)

@app.get('/')
def get_root():
    response = "<html><body><pre>"
    apps = cf('/v2/apps')

    for app in apps['resources']:
        name = app['entity']['name']
        created_at = app['metadata']['created_at']
        updated_at = app['metadata']['updated_at']
        buildpack = app['entity']['buildpack']
        detected_buildpack = app['entity']['detected_buildpack']
        if buildpack is None: 
            buildpack = detected_buildpack
            #org = get_org(app['entity']['org_guid'])
            org = "foo"
            space = api_cache(app['entity']['space_url'])
            org = api_cache(space['entity']['organization_url'])
            routes = cf(app['entity']['routes_url'])
            
            response += str("App: " + name + " Buildpack: " +  buildpack + " created at " + created_at + " updated at " + updated_at)
            response += str("\tOrg: " + org['entity']['name'] + " Space: " + org['entity']['name'])
            response += ("Routes:")
            for route in routes['resources']:
                host = route['entity']['host']
                domain = api_cache(route['entity']['domain_url'])
                response += ("\t" + host + "." + domain['entity']['name'])
    response += "</pre></body></html>"
    return response
                
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port)