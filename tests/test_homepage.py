import archie
import os
import tempfile
import logging

def test_visit_homepage():
    app = archie.webapp.get_flask_app()
    app.config['DEBUG'] = True
    app.config['TESTING'] = True
    client = app.test_client()
    app.set_payload_handler('')
    r = client.get('/')
    assert b'Uncle Archie' in r.data

