from .utils import post_pingpong_webhook, post_pr_webhook, extract_payload
import archie
import logging
import os, sys
import json
import unittest

class TestPayload(unittest.TestCase):
    def test_webhooks_ok(self):
        """
        Test that the Uncle Archie webhook server returns status 200
        """
        archie.webapp.app.config['debug'] = True
        archie.webapp.app.config['DEBUG'] = True
        archie.webapp.app.config['TESTING'] = True
        client = archie.webapp.app.test_client()
        archie.webapp.app.set_payload_handler('')
    
        r = post_pr_webhook(client)
        self.assertEqual(r.status_code,200)
    
    def test_ping_webhook(self):
        """
        Test that the Uncle Archie webhook server plays ping pong
        """
        archie.webapp.app.config['DEBUG'] = True
        archie.webapp.app.config['TESTING'] = True
        client = archie.webapp.app.test_client()
        archie.webapp.app.set_payload_handler('')
    
        r = post_pingpong_webhook(client)
        self.assertEqual(r.status_code,200)
    
        d = extract_payload(r)
        self.assertIn('msg',d.keys())
        self.assertEqual(d['msg'],'pong')
    
    def test_pr_webhooks_ok(self):
        """
        Test that the Uncle Archie webhook server correctly processes PR webhooks
        """
        # assertLogs
        # https://docs.python.org/3/library/unittest.html#unittest.TestCase.assertLogs
        archie.webapp.app.config['DEBUG'] = True
        archie.webapp.app.config['TESTING'] = True
        client = archie.webapp.app.test_client()
        archie.webapp.app.set_payload_handler('pr_test')
    
        r = post_pr_webhook(client)
        self.assertEqual(r.status_code,200)
    
        self.assertLogs('Is pull request open? False')
        self.assertLogs('Is pull request sync? True')
        self.assertLogs('Is pull request close? False')
        self.assertLogs('Is this a merge commit? True')
        self.assertLogs('Pull request number 81')
        self.assertLogs('Pull request head commit: 48480b8022182a487e27c5f54ac1726da8e654e1')
        self.assertLogs('Short repo name: private-www')
        self.assertLogs('Full repo name: dcppc/private-www')
        self.assertLogs('Repo clone url: https://github.com/dcppc/private-www.git')
        self.assertLogs('Repo ssh url: git@github.com:dcppc/private-www.git')
        self.assertLogs('Repo html url: https://github.com/dcppc/private-www')


