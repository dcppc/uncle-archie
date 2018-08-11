import subprocess
from subprocess import PIPE
import tempfile
import json, os, re
from github import Github, GithubException

"""
private-www Integration Test CI Hook for Uncle Archie

This hook should be installed into all submodules of private-www.
When a pull request in any of these submodules is updated, and that 
pull request has a label "Run private-www integration test",
we run a CI test and update the status of the head commit on the PR.

If the build succeeds, the commit is marked as having succeed.
Otherwise the commit is marked as failed.
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
            'repo_whitelist' : ['dcppc/internal','dcppc/organize','dcppc/nih-demo-meetings'],
            'task_name' : 'Uncle Archie private-www Integration Test',
            'pass_msg' : 'The private-www integration test passed!',
            'fail_msg' : 'The private-www integration test failed.',
    }

    # This must be a pull request
    if ('pull_request' not in payload.keys()) or ('action' not in payload.keys()):
        return

    # We are only interested in PRs that have the label
    # ""Run private-www integration test"
    pr_labels = payload['pull_request']['labels']
    if 'Run private-www integration test' not in pr_labels:
        return

    # We are only interested in PRs that are
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
    head_commit = payload['pull_request']['head']['sha']
    pull_number = payload['number']

    # Use Github access token to get API instance
    token = config['github_access_token']
    g = Github(token)
    r = g.get_repo(full_repo_name)
    c = r.get_commit(head_commit)

    # -----------------------------------------------
    # start private-www integration test build
    logging.info("Starting private-www integration test build for submodule %s"%(full_repo_name))

    # Strategy:
    # * This will _always_ use private-www  as the build repo
    # * This will _always_ clone recursively
    # * This will _only_ update the submodule of interest,
    #   to the head commit of the pull request.
    # * This will run mkdocs on the entire private-www site.


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

    # This is always the repo we clone
    ghurl = "git@github.com:dcppc/private-www"

    clonecmd = ['git','clone','--recursive',ghurl]
    logging.debug("Runing clone cmd %s"%(' '.join(clonecmd)))
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

        # We are always using the latest version of private-www,
        # of the default branch, so no need to check out any version.

        # However, we do want to check out the correct submodule commit
        # in the docs/ folder before we test the mkdocs build command.
        # That's what triggered this test in the first place - one of the 
        # submodules was updated in a PR. Make the submodule point
        # to the head commit of that PR.

        # Assemble submodule directory by determining which submdule
        # was updated from the payload (repo_name)
        repo_dir = os.path.join(scratch_dir, repo_name)
        docs_dir = os.path.join(repo_dir,'docs')
        submodule_dir = os.path.join(docs_dir,repo_name)

        cocmd = ['git','checkout',head_commit]
        logging.debug("Runing checkout cmd %s from %s"%(' '.join(cocmd), submodule_dir))
        coproc = subprocess.Popen(
                cocmd,
                stdout=PIPE, 
                stderr=PIPE, 
                cwd=submodule_dir
        )
        if check_for_errors(coproc):
            build_status = "fail"
            abort = True

    if not abort:
        buildcmd = ['mkdocs','build']
        logging.debug("Runing build command %s"%(' '.join(buildcmd)))
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
        logging.info("private-www integration test succes:")
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
        logging.info("private-www integration test failure:")
        logging.info("    Commit %s"%commit)
        logging.info("    PR %s"%pull_number)
        logging.info("    Repo %s"%full_repo_name)
        return



def check_for_errors(proc):
    out = proc.stdout.read().decode('utf-8').lower()
    err = proc.stderr.read().decode('utf-8').lower()

    if "exception" in out or "exception" in err:
        return True

    if "error" in out or "error" in err:
        return True

    return False


