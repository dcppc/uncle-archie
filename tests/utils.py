import os
import json
import logging


HEADERS = {
        'Content-type' : 'application/json',
        'Accept' : 'text/plain'
}

base = os.path.split(os.path.abspath(__file__))[0]


######################################
# Load and extract payloads


def load_from_museum(fname):
    """
    Load a payload named fname from ../museum
    """
    fname = os.path.join(base,'..','museum',fname)
    logging.info("Opening file %s"%(fname))
    d = {}
    with open(fname,'r') as f:
        d = json.load(f)
    return d


def extract_payload(request):
    """
    Given the reult of a flask client request,
    extract payload as JSON and return as dict
    """
    result = request.data.decode('utf-8')
    d = json.loads(result)
    return d


######################################
# Functions to post webhooks


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
    Fake pull request webhook (sync event)
    """
    return post_pr_sync_webhook(client)


def post_new_branch_webhook(client):
    """
    Commit that creates a new branch
    """
    # Get webhook from file
    d = load_from_museum('new_branch_event.json')

    # Post the webhook
    return client.post(
            '/',
            json=d,
            headers=HEADERS,
    )


def post_close_pr_webhook(client):
    """
    Commit that closes a pull request
    """
    # Get webhook from file
    d = load_from_museum('push_pr_to_master_1.json')

    # Post the webhook
    return client.post(
            '/',
            json=d,
            headers=HEADERS,
    )


def post_pr_commit_to_master_webhook(client):
    """
    Commit that merges a pull request onto master
    """
    # Get webhook from file
    d = load_from_museum('push_pr_to_master_2.json')

    # Post the webhook
    return client.post(
            '/',
            json=d,
            headers=HEADERS,
    )

def post_pr_sync_webhook(client):
    """
    Commit that syncs an existing PR
    """
    # Get webhook from file
    d = load_from_museum('sync_pr_event.json')

    # Post the webhook
    return client.post(
            '/',
            json=d,
            headers=HEADERS
    )


