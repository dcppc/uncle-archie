import archie
import os
import tempfile
import logging

def visit_homepage(client):
    return client.get('/')

def test_visit_homepage():
    archie.webapp.app.config['DEBUG'] = True
    archie.webapp.app.config['TESTING'] = True
    client = archie.webapp.app.test_client()
    archie.webapp.app.set_payload_handler('')
    r = visit_homepage(client)
    print(r.data)
    assert b'Uncle Archie' in r.data
