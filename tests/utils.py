import os
import json


HEADERS = {
        'Content-type' : 'application/json',
        'Accept' : 'text/plain'
}

base = os.path.split(os.path.abspath(__file__))[0]


def extract_payload(request):
    """
    Given the reult of a flask client request,
    extract payload as JSON and return as dict
    """
    result = request.data.decode('utf-8')
    d = json.loads(result)
    return d


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

