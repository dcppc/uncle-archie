import archie
import os, sys
import tempfile
import logging

root = logging.getLogger()
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
root.addHandler(ch)

def visit_homepage(client):
    return client.get('/')

def test_visit_homepage():
    archie.webapp.app.config['debug'] = True
    archie.webapp.app.config['DEBUG'] = True
    archie.webapp.app.config['TESTING'] = True
    client = archie.webapp.app.test_client()
    r = visit_homepage(client)
    print(r.data)
    assert b'Uncle Archie' in r.data
