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


logging.basicConfig(filename='/tmp/uncle_archie.log',
                    filemode='a',
                    level=logging.DEBUG)


@app.route('/webhook', methods=['GET', 'POST'])
def index():
    """
    Main WSGI application entry.
    """
    path = os.path.dirname(os.path.abspath(__file__))

    # Only POST is implemented
    if request.method != 'POST':
        logging.error('ERROR: Only POST method is implemented')
        abort(501)

    # Load config
    with open(os.path.join(path, 'config.json'), 'r') as cfg:
        config = json.loads(cfg.read())

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
    if secret!='':
        try:
            if payload['secret'] != secret:
                logging.error('Invalid secret %s.'%(payload['secret']))
                abort(403)
        except:
            abort(501)

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

    process_payload(payload,meta)

    # And done.
    ##############################

    # Clean up
    return json.dumps({'status':'done'})



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

