import archie
import json
import os, sys
import tempfile
import logging

base = os.path.split(os.path.abspath(__file__))[0]

root = logging.getLogger()
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
root.addHandler(ch)

def post_webhook(client):

    fname = os.path.join(base,'..','museum','pr_sync.json')

    print("Opening file %s"%(fname))
    d = {}
    with open(fname,'r') as f:
        d = json.load(f)

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    return client.post(
            '/',
            json=d,
            headers=headers,
    )

def test_visit_homepage():
    archie.webapp.app.config['debug'] = True
    archie.webapp.app.config['DEBUG'] = True
    archie.webapp.app.config['TESTING'] = True
    client = archie.webapp.app.test_client()
    r = post_webhook(client)
    print(r.data)
    assert True

