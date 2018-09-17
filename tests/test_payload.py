from .utils import post_pingpong_webhook, post_pr_webhook, extract_payload
import archie
import logging
import os, sys
import json

def test_webhooks_ok():
    archie.webapp.app.config['debug'] = True
    archie.webapp.app.config['DEBUG'] = True
    archie.webapp.app.config['TESTING'] = True
    client = archie.webapp.app.test_client()
    archie.webapp.app.set_payload_handler('')

    r = post_pr_webhook(client)
    assert r.status_code==200

def test_ping_webhook():
    archie.webapp.app.config['debug'] = True
    archie.webapp.app.config['DEBUG'] = True
    archie.webapp.app.config['TESTING'] = True
    client = archie.webapp.app.test_client()
    archie.webapp.app.set_payload_handler('')

    r = post_pingpong_webhook(client)
    assert r.status_code==200

    d = extract_payload(r)
    assert 'msg' in d.keys()
    assert d['msg']=='pong'

def test_pr_webhooks_ok():
    archie.webapp.app.config['debug'] = True
    archie.webapp.app.config['DEBUG'] = True
    archie.webapp.app.config['TESTING'] = True
    client = archie.webapp.app.test_client()
    archie.webapp.app.set_payload_handler('pr_test')

    r = post_pr_webhook(client)
    assert r.status_code==200

