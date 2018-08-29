import json, os, re
from github import Github, GithubException

"""
Use Case Library Snakemake Test CI Hook for Uncle Archie

Repository: dcppc/use-case-library
Webhook event: pull requests created/updated

Description:
This hook detects when pull requests are opened or updated
in the use case library, and runs the snakemake build step.
If the build works, the commit is marked success.

Process:
- get repo/commiter/branch name/latest commit id
- run command
- update commit status
"""

def process_payload(payload,meta,config):
    """
    Look for events that are pull requests
    being opened or updated. Find the head
    commit and mark it as "passed".
    """

    # Set parameters for the PR builder
    params = {
            'repo_whitelist' : ['dcppc/use-case-library'],
            'task_name' : 'Uncle Archie Pull Request Tester',
            'pass_descr' : 'This is a rubber stamp PR approval.'
    }

    # This must be a pull request
    if 'pull_request' not in payload.keys():
        return

    if 'action' not in payload.keys():
        return

    if payload['action'] not in ['opened','synchronize']:
        # we are only interested in PRs that are
        # being opened or updated
        return

    # This must be a whitelisted repo
    repo_name = payload['repository']['name']
    full_repo_name = payload['repository']['full_name']
    if full_repo_name not in params['repo_whitelist']:
        return

    # Keep it simple:
    # get the head commit
    # and mark it as okay
    head_commit = payload['pull_request']['head']['sha']
    pull_number = payload['number']

    # Use Github access token to get API instance
    token = config['github_access_token']
    g = Github(token)
    r = g.get_repo(full_repo_name)
    c = r.get_commit(head_commit)

    # -----------------------------------------------



    # This is where we would clone into our workspace,
    # or otherwise do actual work.



    # -----------------------------------------------

    try:
        commit_status = c.create_status(
                state = "success",
                description = params['pass_descr'],
                context = params['task_name']
        )

    except GithubException as e:
        from datetime import datetime
        right_now = datetime.now().isoformat()
        tmpfile = "tmp_%s"%(right_now)
        with open('/tmp/archie/rubberstamp_commitstatus_FAIL_%s'%(tmpfile),'w') as f:
            f.write("The commit status failed to update.\n")
            f.write(repr(e))
        return

    from datetime import datetime
    right_now = datetime.now().isoformat()
    tmpfile = "tmp_%s"%(right_now)
    with open('/tmp/archie/rubberstamp_commitstatus_%s'%(tmpfile),'w') as f:
        f.write("The commit status was updated successfully.\n")


if __name__=="__main__":
    process_payload({'type':'test','name':'private_www'},{'a':1,'b':2})


