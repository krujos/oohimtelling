#!/usr/bin/env python
from __future__ import print_function
import json 
import requests 
import sys
import os
import time
from flask import Flask, request, Response
from flask import jsonify
from functools import wraps

Flask.get = lambda self, path: self.route(path, methods=['get'])


##################################The Setup###############################################
vcap_services = json.loads(os.getenv("VCAP_SERVICES"))
client_id = None
client_secret = None
uaa_uri = None
api = None
cache = dict() 
port = 8003
expire_time = 0
token = None

if 'PORT' in os.environ:
    port = int(os.getenv("PORT"))

app = Flask(__name__)

for service in vcap_services['user-provided']:
    if 'uaa' == service['name']:
        client_id = service['credentials']['client_id']
        client_secret = service['credentials']['client_secret']
        uaa_uri = service['credentials']['uri']
    elif 'cloud_controller' == service['name']:
        api = service['credentials']['uri']
###################################The Auth##############################################

def check_auth(user, password): 
    return user == client_id and password == client_secret
    
def authenticate(): 
    return Response('You must be authenticated to use this application', 401, 
    {"WWW-Authenticate": 'Basic realm="Login Required"'})
    
def requires_auth(f): 
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

##############################The bidness logic##########################################
def get_token():
    global expire_time, token
    if expire_time < time.time(): 
        client_auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
        r = requests.get(url=uaa_uri, headers={'accept': 'application/json'},
            params={'grant_type': 'client_credentials'}, auth=client_auth, verify=False)
        expire_time = time.time() + (int(r.json()['expires_in']) - 60) 
        token = r.json()['access_token']
        print( "Token expires at " + str(expire_time))
        
    return token 
    
def cf(path):
    access_token="bearer " + get_token()
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
    
###################################Controllers#################################
    
@app.get('/apps')
@requires_auth
def get_root():
    return jsonify(apps=get_apps())
                
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port, debug=True)