import os
import json


HEADERS = {
        'Content-type' : 'application/json',
        'Accept' : 'text/plain'
}

base = os.path.split(os.path.abspath(__file__))[0]


def post_pingpong_webhook(client):
    """
    Post a ping webhook
    """
    # Set the header
    headers = HEADERS
    headers['X-Github-Event'] = 'ping'

    d = {}

    # Post the webhook
    return client.post(
            '/',
            json=d,
            headers=headers,
    )


def post_pr_webhook(client):
    """
    Post a fake pull request webhook
    """
    # Get webhook from file
    fname = os.path.join(base,'..','museum','pr_sync.json')
    print("Opening file %s"%(fname))
    d = {}
    with open(fname,'r') as f:
        d = json.load(f)

    # Post the webhook
    return client.post(
            '/',
            json=d,
            headers=HEADERS,
    )

