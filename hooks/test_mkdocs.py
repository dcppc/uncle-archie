import subprocess
from subprocess import PIPE
import tempfile
import logging
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
            'repo_whitelist' : ['charlesreid1/search-demo-mkdocs-material',
                                'dcppc/private-www'],
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

    # Remember: you can only read() the output
    # of a PIPEd process once.

    abort = False

    # the repo must be on github
    ghurl = "git@github.com:%s"%(full_repo_name)
    logging.info("Cloning repo at %s"%(ghurl))

    # Note that this checks out repos
    # using the SSH keys in ~/.ssh
    # and the github username in ~/.extras
    # 
    # If you push any changes, make sure you
    # change your user first!
    # https://help.github.com/articles/setting-your-username-in-git/

    clonecmd = ['git','clone','--recursive',ghurl]
    cloneproc = subprocess.Popen(
            clonecmd, 
            stdout=PIPE, 
            stderr=PIPE, 
            cwd=scratch_dir
    )
    if check_for_errors(cloneproc,"git clone"):
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
        if check_for_errors(coproc,"git checkout"):
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
        if check_for_errors(buildproc,"mkdocs build"):
            build_status = "fail"
            abort = True
        else:
            # the only test that mattered, passed
            build_status = "pass"

    ###############
    # clean up.
    ###############

    logging.info("Cleaning up after repo %s"%(full_repo_name))
    subprocess.call(['rm','-fr',scratch_dir])

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
        logging.info("    Commit %s"%head_commit)
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



def check_for_errors(proc,label):
    out = proc.stdout.read().decode('utf-8').lower()
    err = proc.stderr.read().decode('utf-8').lower()

    logging.info("Results from process %s:"%(label))
    logging.info("%s"%(out))
    logging.info("%s"%(err))

    if "exception" in out or "exception" in err:
        return True

    if "error" in out or "error" in err:
        return True

    return False

