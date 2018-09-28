import subprocess
import logging
from subprocess import PIPE
import tempfile
import json, os, re
from github import Github, GithubException
from datetime import datetime

"""
four-year-plan Build Test CI Hook for Uncle Archie

This hook should be installed in the four-year-plan repository.
This will use snakemake to attempt to build the site.

If the build succeeds, the commit is marked as having succeed.
Otherwise the commit is marked as failed.
"""

HTDOCS="/www/archie.nihdatacommons.us/htdocs"

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
            'repo_whitelist' : ['dcppc/four-year-plan'],
            'task_name' : 'Uncle Archie four-year-plan Build Test',
            'pass_msg' : 'The four-year-plan build test passed!',
            'fail_msg' : 'The four-year-plan build test failed.',
    }

    # This must be a pull request
    if ('pull_request' not in payload.keys()) or ('action' not in payload.keys()):
        return

    # This must be a whitelisted repo
    repo_name = payload['repository']['name']
    full_repo_name = payload['repository']['full_name']
    if full_repo_name not in params['repo_whitelist']:
        logging.debug("Skipping four-year-plan build test: this is not the four-year-plan repo")
        return

    # We are only interested in PRs that are
    # being opened or updated
    if payload['action'] not in ['opened','synchronize']:
        logging.debug("Skipping four-year-plan build test: this is not opening/updating a PR")
        return

    if payload['pull_request']['base']['ref']=='gh-pages':
        logging.debug("Skipping four-year-plan build test because PR is based on gh-pages branch")
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
    # start four-year-plan build test with snakemake

    logging.info("Starting four-year-plan build test build")

    # Strategy:
    # * This will _always_ use four-year-plan  as the build repo
    # * This will _always_ clone recursively
    # * This will _only_ update the submodule of interest,
    #   to the head commit of the pull request.
    # * This will run mkdocs on the entire four-year-plan site.


    unique = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_filename = "four_year_plan_build_test_%s"%(unique)


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
    ghurl = "git@github.com:dcppc/four-year-plan"

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
    status_failed, status_file = record_and_check_output(cloneproc,"git clone",unique_filename)
    if status_failed:
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
        status_failed, status_file = record_and_check_output(coproc,"git checkout",unique_filename)
        if status_failed:
            build_status = "fail"
            abort = True

    # In case of new submodule
    if not abort:
        sucmd = ['git','submodule','update','--init']
        suproc = subprocess.Popen(
                sucmd,
                stdout=PIPE, 
                stderr=PIPE, 
                cwd=repo_dir
        )
        status_failed, status_file = record_and_check_output(suproc,"submodule update",unique_filename)
        if status_failed:
            build_status = "fail"
            abort = True

    if not abort:
        buildcmd = ['snakemake','--nocolor','build_docs']
        buildproc = subprocess.Popen(
                buildcmd, 
                stdout=PIPE,
                stderr=PIPE, 
                cwd=repo_dir
        )
        status_failed, status_file = record_and_check_output(buildproc,"snakemake build",unique_filename)
        if status_failed:
            build_status = "fail"
        else:
            # the only test that mattered, passed
            build_status = "pass"

    # end snakemake build
    # -----------------------------------------------


    # This is where we add a second status update 
    # and copy the mkdocs output to the htdocs dir

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

        logging.info("four-year-plan build test succes:")
        logging.info("    Commit %s"%head_commit)
        logging.info("    PR %s"%pull_number)
        logging.info("    Repo %s"%full_repo_name)
        logging.info("    Link %s"%status_url)
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

        logging.info("four-year-plan build test failure:")
        logging.info("    Commit %s"%head_commit)
        logging.info("    PR %s"%pull_number)
        logging.info("    Repo %s"%full_repo_name)
        logging.info("    Link %s"%status_url)
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

    out = proc.stdout.read().decode('utf-8')
    err = proc.stderr.read().decode('utf-8')

    lout = out.lower()
    lerr = err.lower()

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

    # Here - we need to be more careful.
    # Commit messages can contain exception or error.

    if "exception" in lout or "exception" in lerr:
        return True, unique_filename

    if "error" in lout or "error" in lerr:
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


