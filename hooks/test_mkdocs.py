import subprocess
from subprocess import PIPE
import tempfile
import json, os, re
from github import Github, GithubException

"""
Mkdocs Documentation Tester CI Hook for Uncle Archie

This hook checks out a particular commit in a repo,
and attempts to build the mkdocs documentation from it. 

If the build succeeds, the commit is marked as having succeed.
"""

def process_payload(payload, meta, config):
    """
    Look for events that are pull requests being opened or updated. 
    Clone the repo (recursively). 
    Find the head commit and check it out.
    Build the docs.
    Examine output for failures.
    Mark the commit pass/fail.
    """
    # Set parameters for the PR builder
    params = {
            'repo_whitelist' : ['charlesreid1/search-demo-mkdocs-material'],
            'task_name' : 'Uncle Archie Mkdocs Tester',
            'pass_msg' : 'The mkdocs build test passed!',
            'fail_msg' : 'The mkdocs build test failed.',
    }

    # This must be a pull request
    if ('pull_request' not in payload.keys()) or ('action' not in payload.keys()):
        return

    # we are only interested in PRs that are
    # being opened or updated
    if payload['action'] not in ['opened','synchronize']:
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
    # start mkdocs build


    ######################
    # logic. noise.
    ######################

    # Fail by default!
    build_status = "fail"
    build_msg = "" # if blank at the end, use the default


    ######################
    # make space.
    ######################

    scratch_dir = tempfile.mkdtemp()
    FNULL = open(os.devnull, 'w')


    ######################
    # build.
    ######################

    abort = False

    # the repo must be on github
    ghurl = "https://github.com/%s"%full_repo_name

    clonecmd = ['git','clone','--recursive',ghurl]
    cloneproc = subprocess.Popen(
            clonecmd, 
            stdout=PIPE, 
            stderr=PIPE, 
            cwd=scratch_dir
    )
    if check_for_errors(cloneproc):
        build_status = "fail"
        abort = True

    if not abort:
        repo_dir = os.path.join(scratch_dir, repo_name)

        cocmd = ['git','checkout',head_commit]
        coproc = subprocess.Popen(
                cocmd,
                stdout=PIPE, 
                stderr=PIPE, 
                cwd=repo_dir
        )
        if check_for_errors(coproc):
            build_status = "fail"
            abort = True

    if not abort:
        buildcmd = ['mkdocs','build']
        buildproc = subprocess.Popen(
                buildcmd, 
                stdout=PIPE,
                stderr=PIPE, 
                cwd=repo_dir
        )
        if check_for_errors(buildproc):
            build_status = "fail"
            abort = True
        else:
            # the only test that mattered, passed
            build_status = "pass"

    # end mkdocs build
    # -----------------------------------------------

    if build_status == "pass":

        if build_msg == "":
            build_msg = params['pass_msg']

        commit_status = c.create_status(
                        state = "success",
                        description = build_msg,
                        context = params['task_name']
        )
        logging.info("Uncle Archie: mkdocs build failure:")
        logging.info("    Commit %s"%commit)
        logging.info("    PR %s"%pull_number)
        logging.info("    Repo %s"%full_repo_name)
        return

    elif build_status == "fail":

        if build_msg == "":
            build_msg = params['fail_msg']

        commit_status = c.create_status(
                        state = "failure",
                        description = build_msg,
                        context = params['task_name']
        )
        logging.info("Uncle Archie: mkdocs build failure:")
        logging.info("    Commit %s"%commit)
        logging.info("    PR %s"%pull_number)
        logging.info("    Repo %s"%full_repo_name)
        return

        ###from datetime import datetime
        ###right_now = datetime.now().isoformat()
        ###tmpfile = "tmp_%s"%(right_now)
        ###with open('/tmp/archie/testmkdocs_FAIL_%s'%(tmpfile),'w') as f:
        ###    f.write("The commit status failed to update.\n")
        ###    f.write(repr(e))
        ###return


def check_for_errors(proc):
    if "exception" in proc.stdout.read().decode('utf-8').lower() \
    or "exception" in proc.stderr.read().decode('utf-8').lower():
        return True
    if "error" in proc.stdout.read().decode('utf-8').lower() \
    or "error" in proc.stderr.read().decode('utf-8').lower():
        return True
    else:
        return False

