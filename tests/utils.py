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
    Load a payload named fname from payloads museum
    in ../payloads
    """
    fname = os.path.join(base,'..','payloads',fname)
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



def post_pr_opened(client):
    """
    Pull request pull request webhook (sync event)
    """
    # Get webhook from file
    d = load_from_museum('PullRequestEvent/action_opened.json')

    # Post the webhook
    return client.post(
            '/',
            json=d,
            headers=HEADERS,
    )


def post_pr_closed_merged(client):
    """
    Webhook for closing a PR by merging it
    """
    # Get webhook from file
    d = load_from_museum('PullRequestEvent/action_closed_merged.json')

    # Post the webhook
    return client.post(
            '/',
            json=d,
            headers=HEADERS,
    )

def post_pr_closed_unmerged(client):
    """
    Webhook for closing a PR without merging it
    """
    # Get webhook from file
    d = load_from_museum('PullRequestEvent/action_closed_unmerged.json')

    # Post the webhook
    return client.post(
            '/',
            json=d,
            headers=HEADERS,
    )


def post_pr_sync(client):
    """
    Commit that syncs an existing PR
    """
    # Get webhook from file
    d = load_from_museum('PullRequestEvent/action_synchronize.json')

    # Post the webhook
    return client.post(
            '/',
            json=d,
            headers=HEADERS
    )


