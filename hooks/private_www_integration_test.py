import subprocess
import logging
from subprocess import PIPE
import tempfile
import json, os, re
from github import Github, GithubException
from datetime import datetime

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
    pr_labels = [d['name'] for d in payload['pull_request']['labels']]
    if 'Run private-www integration test' not in pr_labels:
        logging.debug("Skipping private-www integration test: this PR is not labeled with \"Run private-www integration test\"")
        return

    # We are only interested in PRs that are
    # being opened or updated
    if payload['action'] not in ['opened','synchronize']:
        logging.debug("Skipping private-www integration test: this is not opening/updating a PR")
        return

    # This must be a whitelisted repo
    repo_name = payload['repository']['name']
    full_repo_name = payload['repository']['full_name']
    if full_repo_name not in params['repo_whitelist']:
        logging.debug("Skipping private-www integration test: this is not a whitelisted repo")
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
    logging.debug("Running clone cmd %s"%(' '.join(clonecmd)))
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

        # We are always using the latest version of private-www,
        # of the default branch, so no need to check out any version.

        # However, we do want to check out the correct submodule commit
        # in the docs/ folder before we test the mkdocs build command.
        # That's what triggered this test in the first place - one of the 
        # submodules was updated in a PR. Make the submodule point
        # to the head commit of that PR.

        # Assemble submodule directory by determining which submdule
        # was updated from the payload (repo_name)
        repo_dir = os.path.join(scratch_dir, "private-www")
        docs_dir = os.path.join(repo_dir,'docs')
        submodule_dir = os.path.join(docs_dir,repo_name)

        cocmd = ['git','checkout',head_commit]
        logging.debug("Running checkout cmd %s from %s"%(' '.join(cocmd), submodule_dir))
        coproc = subprocess.Popen(
                cocmd,
                stdout=PIPE, 
                stderr=PIPE, 
                cwd=submodule_dir
        )
        if check_for_errors(coproc,"git checkout"):
            build_status = "fail"
            abort = True

    if not abort:
        buildcmd = ['snakemake','build']
        logging.debug("Running build command %s"%(' '.join(buildcmd)))
        buildproc = subprocess.Popen(
                buildcmd, 
                stdout=PIPE,
                stderr=PIPE, 
                cwd=repo_dir
        )
        # save the output first
        status_failed, status_file = record_and_check_output(buildproc,"snakemake build")
        if status_failed:
            build_status = "fail"
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
        logging.info("private-www integration test failure:")
        logging.info("    Commit %s"%head_commit)
        logging.info("    PR %s"%pull_number)
        logging.info("    Repo %s"%full_repo_name)
        return


def record_and_check_output(proc,label):
    """
    Given a process, get the stdout and stderr streams
    and record them in an output file that can be provided
    to users as a link. Also return a boolean on whether
    there was a problem with the process.

    Run this function on the last/most important step
    in your CI test. 
    """ 
    unique = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_filename = "ucl_snakemake_test_%s"%(unique)

    output_path = os.path.join(HTDOCS,'output')
    output_file = os.path.join(output_path,unique_filename)

    out = proc.stdout.read().decode('utf-8').lower()
    err = proc.stderr.read().decode('utf-8').lower()

    lines = [ "======================\n",
              "======= STDOUT =======\n",
              out,
              "\n\n",
              "======================\n",
              "======= STDERR =======\n",
              err,
              "\n\n"]

    with open(output_file,'w') as f:
        [f.write(j) for j in lines]

    logging.info("Results from process %s:"%(label))
    logging.info("%s"%(out))
    logging.info("%s"%(err))
    logging.info("Recorded in file %s"%(output_file))

    if "exception" in out or "exception" in err:
        return True, unique_filename

    if "error" in out or "error" in err:
        return True, unique_filename

    return False, unique_filename


def check_for_errors(proc,label):
    """
    Given a process, get the stdout and stderr streams and look for
    exceptions or errors.  Return a boolean whether there was a problem.
    """ 
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


