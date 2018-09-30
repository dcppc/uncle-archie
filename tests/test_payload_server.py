import archie

from .utils import \
        extract_payload, \
        post_pingpong_webhook, \
        post_pr_opened, \
        post_pr_closed_merged, \
        post_pr_closed_unmerged, \
        post_pr_sync

import logging
import os, sys
import json
import unittest

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
    
        r = post_pr_opened(client)
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
    
        r = post_pingpong_webhook(client)
        self.assertEqual(r.status_code,200)
    
        d = extract_payload(r)
        self.assertIn('msg',d.keys())
        self.assertEqual(d['msg'],'pong')
    
