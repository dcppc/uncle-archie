import subprocess
import logging
from subprocess import PIPE
import tempfile
import json, os, re
from github import Github, GithubException
from datetime import datetime

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

HTDOCS="/www/archie.nihdatacommons.us/htdocs"

def process_payload(payload,meta,config):
    """
    Look for events that are pull requests
    being opened or updated. Find the head
    commit and mark it as "passed".
    """

    # Set parameters for the PR builder
    params = {
            'repo_whitelist' : ['dcppc/use-case-library'],
            'task_name' : 'Uncle Archie Use Case Library Pull Request Tester',
            'pass_msg' : 'The use-case-library build test passed!',
            'fail_msg' : 'The use-case-library build test failed.',
    }

    # This must be a pull request
    if 'pull_request' not in payload.keys():
        return

    if 'action' not in payload.keys():
        return

    # This must be a whitelisted repo
    repo_name = payload['repository']['name']
    full_repo_name = payload['repository']['full_name']
    if full_repo_name not in params['repo_whitelist']:
        logging.debug("Skipping use-case-library integration test: this is not the use-case-library repo")
        return

    # We are only interested in PRs that are
    # being opened or updated
    if payload['action'] not in ['opened','synchronize']:
        logging.debug("Skipping use-case-library integration test: this is not opening/updating a PR")
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



    logging.info("Starting use case library build test")

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
    ghurl = "git@github.com:dcppc/use-case-library"

    # Note that this checks out repos
    # using the SSH keys in ~/.ssh
    # and the github username in ~/.extras
    # 
    # If you push any changes, make sure you
    # change your user first!
    # https://help.github.com/articles/setting-your-username-in-git/

    clonecmd = ['git','clone','--recursive',ghurl]
    logging.debug("Running clone cmd %s"%(' '.join(clonecmd)))
    cloneproc = subprocess.Popen(
            clonecmd, 
            stdout=PIPE, 
            stderr=PIPE, 
            cwd=scratch_dir
    )
    status_failed, status_file = record_and_check_output(buildproc,"git clone",unique_filename)
    if 
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
        buildcmd = ['snakemake','build']
        buildproc = subprocess.Popen(
                buildcmd, 
                stdout=PIPE,
                stderr=PIPE, 
                cwd=repo_dir
        )
        # Modify this to save the output first
        status_failed, status_file = record_and_check_output(buildproc,"snakemake build",unique_filename)
        if status_failed:
            build_status = "fail"
        else:
            # the only test that mattered, passed
            build_status = "pass"

    # end snakemake build
    # -----------------------------------------------

    status_url = "https://archie.nihdatacommons.us/output/%s"%(status_file)

    if build_status == "pass":

        if build_msg == "":
            build_msg = params['pass_msg']

        try:
            commit_status = c.create_status(
                            state = "success",
                            target_url = status_url,
                            description = build_msg,
                            context = params['task_name']
            )
        except GithubException as e:
            logging.info("Github error: commit status failed to update.")

        logging.info("use-case-library build test success:")
        logging.info("    Commit %s"%head_commit)
        logging.info("    PR %s"%pull_number)
        logging.info("    Repo %s"%full_repo_name)
        return


    elif build_status == "fail":

        if build_msg == "":
            build_msg = params['fail_msg']

        try:
            commit_status = c.create_status(
                            state = "failure",
                            target_url = status_url,
                            description = build_msg,
                            context = params['task_name']
            )
        except GithubException as e:
            logging.info("Github error: commit status failed to update.")

        logging.info("use-case-library build test failure:")
        logging.info("    Commit %s"%head_commit)
        logging.info("    PR %s"%pull_number)
        logging.info("    Repo %s"%full_repo_name)
        return




def record_and_check_output(proc,label,unique_filename):
    """
    Given a process, get the stdout and stderr streams
    and record them in an output file that can be provided
    to users as a link. Also return a boolean on whether
    there was a problem with the process.

    Run this function on the last/most important step
    in your CI test. 
    """ 
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





if __name__=="__main__":
    process_payload({'type':'test','name':'private_www'},{'a':1,'b':2})


