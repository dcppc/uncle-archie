import archie

import logging
import os, sys
import json
import unittest

"""
Test Uncle Archie Server
(empty payload handler)


This runs a test client-server configuration for the 
Uncle Archie flask server, and tests that the server
returns a 200 code when accessed.
"""

class test_payload_server(unittest.TestCase):
    def test_webhooks_ok(self):
        """
        Test that the Uncle Archie webhook server returns status 200
        """
        app = archie.webapp.get_flask_app()
        app.config['debug'] = True
        app.config['DEBUG'] = True
        app.config['TESTING'] = True
        client = app.test_client()
        app.set_payload_handler('')
    
        r = archie.tests.post_pr_opened(client)
        self.assertEqual(r.status_code,200)
    
    def test_ping_webhook(self):
        """
        Test that the Uncle Archie webhook server plays ping pong
        """
        app = archie.webapp.get_flask_app()
        app.config['DEBUG'] = True
        app.config['TESTING'] = True
        client = app.test_client()
        app.set_payload_handler('')
    
        r = archie.tests.post_pingpong_webhook(client)
        self.assertEqual(r.status_code,200)
    
        d = archie.tests.extract_payload(r)
        self.assertIn('msg',d.keys())
        self.assertEqual(d['msg'],'pong')
    
