from .utils import post_pingpong_webhook, post_pr_webhook
import archie
import logging
import os, sys

def test_webhooks_ok():
    archie.webapp.app.config['debug'] = True
    archie.webapp.app.config['DEBUG'] = True
    archie.webapp.app.config['TESTING'] = True
    client = archie.webapp.app.test_client()
    archie.webapp.app.set_payload_handler('')
    r = post_pr_webhook(client)
    logging.info(r)
    assert r.status_code==200

def test_ping_webhook():
    archie.webapp.app.config['debug'] = True
    archie.webapp.app.config['DEBUG'] = True
    archie.webapp.app.config['TESTING'] = True
    client = archie.webapp.app.test_client()
    archie.webapp.app.set_payload_handler('')
    r = post_pingpong_webhook(client)
    logging.info(r)
    assert r.status_code==200

