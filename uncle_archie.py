import os
import logging
import subprocess
from tempfile import mkstemp
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

logging.basicConfig(filename='/tmp/uncle_archie.log',
                    filemode='a',
                    level=logging.DEBUG)


@app.route('/webhook', methods=['GET', 'POST'])
def index():
    """
    Main WSGI application entry.
    """
    print("Uncle Archie got a visitor!")
    path = os.path.dirname(os.path.abspath(__file__))

    # Only POST is implemented
    if request.method != 'POST':
        return('<h2>hello world</h2>')
        #logging.error('ERROR: Only POST method is implemented')
        #abort(501)

    # Load config
    try:
        pth = os.path.join(path, 'config.json')
        with open(pth, 'r') as cfg:
            config = json.loads(cfg.read())
    except FileNotFoundError:
        logging.error("ERROR: No config file found at %s"%(pth))
        abort(501)

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

    ## payload['secret'] does not exist???
    ## Enforce secret
    #secret = config.get('enforce_secret', '')
    #if secret!='':
    #    try:
    #        if payload['secret'] != secret:
    #            logging.error('Invalid secret %s.'%(payload['secret']))
    #            abort(403)
    #    except:
    #        abort(501)

    # Determining the branch is tricky, as it only appears for certain event
    # types an at different levels
    branch = None
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
        # If the payload structure isn't what we expect, we'll live without
        # the branch name
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
    right_now = datetime.now().isoformat()
    tmpfile = "tmp_%s"%(right_now)
    with open('/tmp/%s'%(tmpfile),'w') as f:
        f.write(str(payload))
    process_payload(payload,meta)

    # And done.
    ##############################

    # Clean up
    return json.dumps({'status':'done'})



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5005)

