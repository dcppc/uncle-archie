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
            'repo_whitelist' : ['dcppc/internal','dcppc/organize','dcppc/nih-demo-meetings','dcppc/dcppc-workshops'],
            'task_name' : 'Uncle Archie private-www Integration Test',
            'pass_msg' : 'The private-www integration test passed!',
            'fail_msg' : 'The private-www integration test failed.',
    }

    # This must be a pull request
    if ('pull_request' not in payload.keys()) or ('action' not in payload.keys()):
        return

    # This must be a whitelisted repo
    repo_name = payload['repository']['name']
    full_repo_name = payload['repository']['full_name']
    if full_repo_name not in params['repo_whitelist']:
        logging.debug("Skipping private-www integration test: this is not a whitelisted repo")
        return

    # We are only interested in PRs that are
    # being opened or updated
    if payload['action'] not in ['opened','synchronize']:
        logging.debug("Skipping private-www integration test: this is not opening/updating a PR")
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


    unique = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_filename = "private_www_integration_test_%s"%(unique)


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
    # clone.
    ######################

    # Remember: you can only read() the output
    # of a PIPEd process once.

    abort = False

    # This is always the repo we clone
    ghurl = "git@github.com:dcppc/private-www"

    clonecmd = ['git','clone','--recursive','-b','master',ghurl]
    logging.debug("Running clone cmd %s"%(' '.join(clonecmd)))
    cloneproc = subprocess.Popen(
            clonecmd, 
            stdout=PIPE, 
            stderr=PIPE, 
            cwd=scratch_dir
    )
    # save the output first
    status_failed, status_file = record_and_check_output(cloneproc,"git clone",unique_filename)
    if status_failed:
        build_status = "fail"
        abort = True

    if not abort:

        # We are always using the latest version of 
        # master branch of private-www,
        # no need to check out any version of
        # private-www.

        # However, we do need to check out
        # a version of the submodule PR that 
        # gtriggered this test.

        # Get the head commit of the PR that
        # triggered this test, and update the
        # appropriate submodule before running
        # snakemake build_docs

        # Assemble submodule directory by determining which submdule
        # was updated from the payload (repo_name)
        repo_dir = os.path.join(scratch_dir, "private-www")

        if repo_name == 'dcppc-workshops':
            submodule_dir_relative = os.path.join('docs','workshops')
        else:
            submodule_dir_relative = os.path.join('docs', repo_name)

        submodule_dir = os.path.join(repo_dir, submodule_dir_relative)

        cocmd = ['git','checkout',head_commit]
        logging.debug("Running checkout cmd %s from %s"%(' '.join(cocmd), submodule_dir))
        coproc = subprocess.Popen(
                cocmd,
                stdout=PIPE, 
                stderr=PIPE, 
                cwd=submodule_dir
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
        logging.debug("Running build command %s"%(' '.join(buildcmd)))
        buildproc = subprocess.Popen(
                buildcmd, 
                stdout=PIPE,
                stderr=PIPE, 
                cwd=repo_dir
        )
        # save the output first
        status_failed, status_file = record_and_check_output(buildproc,"snakemake build",unique_filename)
        if status_failed:
            build_status = "fail"
        else:
            # the only test that mattered, passed
            build_status = "pass"

    # end mkdocs build
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

        logging.info("private-www integration test success:")
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

        logging.info("private-www integration test failure:")
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


