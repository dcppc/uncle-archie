import os
import logging
import subprocess
from tempfile import mkstemp

from ipaddress import ip_address, ip_network

from os import access, remove, fdopen
import requests
import json
from flask import Flask, request, abort

from process_payload import process_payload


"""
Uncle Archie - Flask Server

This is a webhook flask server that serves as a frontend
for Uncle Archie, our home-brewed continuous integration
server.
"""


app = Flask(__name__)
count = 0

logging.basicConfig(filename='/tmp/archie/uncle_archie.log',
                    filemode='a',
                    level=logging.DEBUG)


@app.route('/webhook', methods=['GET', 'POST'])
def index():
    """
    Main WSGI application entry.
    """
    print("Uncle Archie got a visitor!")
    path = os.path.dirname(os.path.abspath(__file__))


    # -----
    # Implement a nice hello world landing page
    if request.method != 'POST':
        # We really need to make a Jinja template instead.
        return('<h2>Hello World! This is Uncle Archie, your local home-brewed CI server.</h2>')


    # -----
    # Load config
    try:
        pth = os.path.join(path, 'config.json')
        with open(pth, 'r') as cfg:
            config = json.loads(cfg.read())
    except FileNotFoundError:
        logging.error("ERROR: No config file found at %s"%(pth))
        abort(501)


    # -----
    # Verify webhooks are from Github
    if 'github_ips_only' in config and config['github_ips_only'] is True:
        whitelist = requests.get('https://api.github.com/meta').json()['hooks']
        for valid_ip in whitelist:
            if src_ip in ip_network(valid_ip):
                break
            else:
                logging.error('IP {} not allowed'.format(src_ip))
                abort(403)


    # -----
    # Implement ping/pong
    event = request.headers.get('X-GitHub-Event', 'ping')
    if event == 'ping':
        return json.dumps({'msg': 'pong'})

    # Gather data
    try:
        payload = request.get_json()

    except Exception:
        logging.warning('Request parsing failed')
        abort(400)




    # Enforce secret
    secret = config.get('enforce_secret', '')
    if secret:
        # Only SHA1 is supported
        header_signature = request.headers.get('X-Hub-Signature')
        if header_signature is None:
            abort(403)

        sha_name, signature = header_signature.split('=')
        if sha_name != 'sha1':
            abort(501)

        # HMAC requires the key to be bytes, but data is string
        mac = hmac.new(str(secret), msg=request.data, digestmod='sha1')

        if not hmac.compare_digest(str(mac.hexdigest()), str(signature)):
            logging.error(' XXXXXXXX A webhook with an invalid secret was received.')
            abort(403)


    # -----
    # Determining the branch is tricky, as it only appears for certain event
    # types an at different levels
    branch = ''
    try:
        # Case 1: a ref_type indicates the type of ref.
        # This true for create and delete events.
        if 'ref_type' in payload:
            if payload['ref_type'] == 'branch':
                branch = payload['ref']

        # Case 2: a pull_request object is involved. This is pull_request and
        # pull_request_review_comment events.
        elif 'pull_request' in payload:
            # This is the TARGET branch for the pull-request, not the source
            # branch
            branch = payload['pull_request']['base']['ref']

        elif event in ['push']:
            # Push events provide a full Git ref in 'ref' and not a 'ref_type'.
            branch = payload['ref'].split('/', 2)[2]


    except KeyError:
        # If the payload structure isn't what we expect, 
        # we'll live without the branch name
        pass

    # All current events have a repository, but some legacy events do not,
    # so let's be safe
    name = payload['repository']['name'] if 'repository' in payload else None

    meta = {
        'name': name,
        'branch': branch,
        'event': event
    }


    ##############################
    # Here, we pass off the hook info
    # to user-defined python functions

    from datetime import datetime
    fname = datetime.now().isoformat()
    with open('/tmp/archie/flask_payload_%s'%(fname),'w') as f:
        f.write(json.dumps(payload,indent=4))

    process_payload(payload,meta,config)

    # And done.
    ##############################

    # Clean up
    return json.dumps({'status':'done'})



if __name__ == '__main__':
    subprocess.call(['mkdir','-p','/tmp/archie/'])
    app.run(host='127.0.0.1', port=5005)

