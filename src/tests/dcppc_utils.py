from .utils import load_from_museum


############################################
# four-year-plan repository payloads

def dcppc_4yp_sync(client):
    """
    Post a webhook event corresponding to
    a push event in the four-year-plan repo
    """
    d = load_from_museum('PullRequestEvent/dcppc_4yp_sync.json')
    return client.post( '/', json=d, headers=HEADERS,)

def dcppc_4yp_closed_merged(client):
    """
    Post a webhook event corresponding to
    a push event in the four-year-plan repo
    """
    d = load_from_museum('PullRequestEvent/dcppc_4yp_closed_merged.json')
    return client.post( '/', json=d, headers=HEADERS,)

def dcppc_4yp_closed_unmerged(client):
    """
    Post a webhook event corresponding to
    a push event in the four-year-plan repo
    """
    d = load_from_museum('PullRequestEvent/dcppc_4yp_closed_unmerged.json')
    return client.post( '/', json=d, headers=HEADERS,)

def dcppc_4yp_push(client):
    """
    Post a webhook event corresponding to
    a push event in the four-year-plan repo
    """
    d = load_from_museum('PushEvent/dcppc_4yp_push.json')
    return client.post( '/', json=d, headers=HEADERS,)



############################################
# internal repository payloads

def dcppc_internal_sync(client):
    """
    Post a webhook event corresponding to
    a push event in the four-year-plan repo
    """
    d = load_from_museum('PullRequestEvent/dcppc_internal_sync.json')
    return client.post( '/', json=d, headers=HEADERS,)

def dcppc_internal_closed_merged(client):
    """
    Post a webhook event corresponding to
    a push event in the four-year-plan repo
    """
    d = load_from_museum('PullRequestEvent/dcppc_internal_closed_merged.json')
    return client.post( '/', json=d, headers=HEADERS,)

def dcppc_internal_closed_unmerged(client):
    """
    Post a webhook event corresponding to
    a push event in the four-year-plan repo
    """
    d = load_from_museum('PullRequestEvent/dcppc_internal_closed_unmerged.json')
    return client.post( '/', json=d, headers=HEADERS,)

def dcppc_internal_push(client):
    """
    Post a webhook event corresponding to
    a push event in the four-year-plan repo
    """
    d = load_from_museum('PushEvent/dcppc_internal_push.json')
    return client.post( '/', json=d, headers=HEADERS,)



############################################
# organize repository payloads

def dcppc_organize_sync(client):
    """
    Post a webhook event corresponding to
    a push event in the four-year-plan repo
    """
    d = load_from_museum('PullRequestEvent/dcppc_organize_sync.json')
    return client.post( '/', json=d, headers=HEADERS,)

def dcppc_organize_closed_merged(client):
    """
    Post a webhook event corresponding to
    a push event in the four-year-plan repo
    """
    d = load_from_museum('PullRequestEvent/dcppc_organize_closed_merged.json')
    return client.post( '/', json=d, headers=HEADERS,)

def dcppc_organize_closed_unmerged(client):
    """
    Post a webhook event corresponding to
    a push event in the four-year-plan repo
    """
    d = load_from_museum('PullRequestEvent/dcppc_organize_closed_unmerged.json')
    return client.post( '/', json=d, headers=HEADERS,)

def dcppc_organize_push(client):
    """
    Post a webhook event corresponding to
    a push event in the four-year-plan repo
    """
    d = load_from_museum('PushEvent/dcppc_organize_push.json')
    return client.post( '/', json=d, headers=HEADERS,)



############################################
# private-www repository payloads

def dcppc_private_www_sync(client):
    """
    Post a webhook event corresponding to
    a commit that updates an existing PR.
    """
    d = load_from_museum('PullRequestEvent/dcppc_private_www_sync.json')
    return client.post( '/', json=d, headers=HEADERS,)

def dcppc_private_www_closed_merged(client):
    """
    Post a webhook event corresponding to
    a closed and merged pull request
    """
    d = load_from_museum('PullRequestEvent/dcppc_private_www_closed_merged.json')
    return client.post( '/', json=d, headers=HEADERS,)

def dcppc_private_www_closed_unmerged(client):
    """
    Post a webhook event corresponding to
    a closed but unmerged pull request
    """
    d = load_from_museum('PullRequestEvent/dcppc_private_www_closed_unmerged.json')
    return client.post( '/', json=d, headers=HEADERS,)

def dcppc_private_www_push(client):
    """
    Post a webhook event corresponding to
    a push event in this repo
    """
    d = load_from_museum('PushEvent/dcppc_private_www_push.json')
    return client.post( '/', json=d, headers=HEADERS,)


############################################
# ucl repository payloads

def dcppc_ucl_sync(client):
    """
    Post a webhook event corresponding to
    a commit that updates an existing PR.
    """
    d = load_from_museum('PullRequestEvent/dcppc_ucl_sync.json')
    return client.post( '/', json=d, headers=HEADERS,)

def dcppc_ucl_closed_merged(client):
    """
    Post a webhook event corresponding to
    a closed and merged pull request
    """
    d = load_from_museum('PullRequestEvent/dcppc_ucl_closed_merged.json')
    return client.post( '/', json=d, headers=HEADERS,)

def dcppc_ucl_closed_unmerged(client):
    """
    Post a webhook event corresponding to
    a closed but unmerged pull request
    """
    d = load_from_museum('PullRequestEvent/dcppc_ucl_closed_unmerged.json')
    return client.post( '/', json=d, headers=HEADERS,)

def dcppc_ucl_push(client):
    """
    Post a webhook event corresponding to
    a push event in this repo
    """
    d = load_from_museum('PushEvent/dcppc_ucl_push.json')
    return client.post( '/', json=d, headers=HEADERS,)



############################################
# workshops repository payloads

def dcppc_workshops_sync(client):
    """
    Post a webhook event corresponding to
    a commit that updates an existing PR.
    """
    d = load_from_museum('PullRequestEvent/dcppc_workshops_sync.json')
    return client.post( '/', json=d, headers=HEADERS,)

def dcppc_workshops_closed_merged(client):
    """
    Post a webhook event corresponding to
    a closed and merged pull request
    """
    d = load_from_museum('PullRequestEvent/dcppc_workshops_closed_merged.json')
    return client.post( '/', json=d, headers=HEADERS,)

def dcppc_workshops_closed_unmerged(client):
    """
    Post a webhook event corresponding to
    a closed but unmerged pull request
    """
    d = load_from_museum('PullRequestEvent/dcppc_workshops_closed_unmerged.json')
    return client.post( '/', json=d, headers=HEADERS,)

def dcppc_workshops_push(client):
    """
    Post a webhook event corresponding to
    a push event in this repo
    """
    d = load_from_museum('PushEvent/dcppc_workshops_push.json')
    return client.post( '/', json=d, headers=HEADERS,)

