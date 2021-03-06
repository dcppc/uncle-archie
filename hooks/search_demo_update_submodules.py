import subprocess
import logging
from subprocess import PIPE
import tempfile
import json, os, re
from github import Github, GithubException
from datetime import datetime


"""
search-demo-mkdocs-material Submodule Update PR for Uncle Archie



Notes:

- search-demo is private-www
- fake-docs is submodule
- install webhooks for uncle archie
- make changes to fake-docs (submodule) and make a pull request
- merge the pull request to trigger the hook function




Description:

This is a bit of an odd "CI test" because it isn't exactly a CI test, but it is
part of a step-by-step CI workflow.

This hook listens for incoming push to master events from fake-docs

When this type of event occurs, the hook opens an "update submodules" PR
in the search-demo-mkdocs-material repo

(At that point, a new webhook is triggered and Uncle Archie will run a continuous
integration test on the newly-opened pull request.)
"""


HTDOCS="/www/archie.nihdatacommons.us/htdocs"

def process_payload(payload, meta, config):
    """
    Look for any push events to the repositories 
    that are search-demo-mkdocs-material submodules.

    When we get a push event, we should figure out
    whether it is on the master branch, and if so, 
    we open a new pull request in search-demo-mkdocs-material
    that updates this submodule.

    Strategy:
    - use the shell, because it will work
    - clone a local copy of private-www
    - create a new branch
    - update submodules
    - push new branch to github
    - use hub (https://hub.github.com/) to create PR from command line

    $ GITHUB_TOKEN="XXXXX" hub pull-request -b charlesreid1:master -h charlesreid1:fix-readme -m 'Fix readme'
    """
    # Set parameters for the submodule update PR opener
    params = {
            'repo_whitelist' : ['charlesreid1/fake-docs'],
            'task_name' : 'Uncle Archie search-demo-mkdocs-material Submodules Update PR',
            'pass_msg' : 'The search-demo-mkdocs-material submodules update PR passed!',
            'fail_msg' : 'The search-demo-mkdocs-material submodules update PR failed.',
    }


    repo_name = payload['repository']['name']
    full_repo_name = payload['repository']['full_name']

    sub_name = payload['repository']['name']
    full_sub_name = payload['repository']['full_name']


    # This must be the use-case-library repo
    if full_repo_name not in params['repo_whitelist']:
        logging.debug("Skipping search demo submodule PR: this is not the search-demo-mkdocs-material repo")
        return

    # This must be a pull request
    if 'pull_request' not in payload.keys():
        logging.debug("Skipping search demo submodule PR: this is not a pull request")
        return

    if 'action' not in payload.keys():
        logging.debug("Skipping search demo submodule PR: this is not a pull request")
        return

    if payload['action']!='closed':
        logging.debug("Skipping search demo submodule PR: this pull request has not been closed yet")
        return

    # We want PRs that are being merged
    if 'merge_commit_sha' not in payload['pull_request']:
        logging.debug("Skipping search demo submodule PR: this pull request was not merged")


    # -----------------------------------------------
    # start private-www submodule update PR 

    logging.info("Starting search demo submodule PR for %s"%(full_repo_name))


    unique = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_filename = "search_demo_update_submodules_%s"%(unique)



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

    parent_repo_name = "search-demo-mkdocs-material"

    # This is always the repo we clone
    parent_repo_url = "git@github.com:charlesreid1/%s"%(parent_repo_name)

    # get the API token
    token = config['github_access_token']

    clonecmd = ['git','clone','--recursive','-b','master',parent_repo_url]
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


    ######################
    # unique branch name
    ######################

    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    branch_name = "update_submodules_%s"%(now)


    ######################
    # Create new branch
    # from master branch HEAD
    ######################

    if not abort:

        repo_dir = os.path.join(scratch_dir, parent_repo_name)

        cocmd = ['git','checkout','-b',branch_name]
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


    ######################
    # Check out the master branch of the submodule
    # and pull the latest changes from upstream
    ######################

    if not abort:

        submodule_dir_relative = os.path.join('docs', repo_name)
        submodule_dir = os.path.join(repo_dir, submodule_dir_relative)

        subcocmd = ['git','checkout','master']
        subcoproc = subprocess.Popen(
                subcocmd,
                stdout=PIPE, 
                stderr=PIPE, 
                cwd=submodule_dir
        )
        status_failed, status_file = record_and_check_output(subcoproc,"git checkout submodule",unique_filename)
        if status_failed:
            build_status = "fail"
            abort = True

        pullcmd = ['git','pull','origin','master']
        pullproc = subprocess.Popen(
                pullcmd,
                stdout=PIPE, 
                stderr=PIPE, 
                cwd=submodule_dir
        )
        status_failed, status_file = record_and_check_output(pullproc,"git pull submodule",unique_filename)
        if status_failed:
            build_status = "fail"
            abort = True


    ######################
    # Add commit push the new submodule
    ######################

    commit_msg = '[Uncle Archie] Updating submodule %s'%(full_sub_name)
    pr_msg = commit_msg 

    if not abort:

        # Add the submodule
        addcmd = ['git','add',submodule_dir_relative]
        addproc = subprocess.Popen(
                addcmd,
                stdout=PIPE,
                stderr=PIPE,
                cwd=repo_dir
        )
        status_failed, status_file = record_and_check_output(addproc,"git add submodule",unique_filename)
        if status_failed:
            build_status = "fail"
            abort = True


        # Commit the new submodule

        commitcmd = ['git','commit',submodule_dir_relative,'-m',commit_msg]
        commitproc = subprocess.Popen(
                commitcmd,
                stdout=PIPE,
                stderr=PIPE,
                cwd=repo_dir
        )
        status_failed, status_file = record_and_check_output(commitproc,"git commit submodule",unique_filename)
        if status_failed:
            build_status = "fail"
            abort = True



        pushcmd = ['git','push','origin',branch_name]
        pushproc = subprocess.Popen(
                pushcmd,
                stdout=PIPE,
                stderr=PIPE,
                cwd=repo_dir
        )
        status_failed, status_file = record_and_check_output(pushproc,"git push origin branch",unique_filename)
        if status_failed:
            build_status = "fail"
            abort = True


    ######################
    # New pull request
    ######################

    if not abort:

        # Store the github token in an environment var for hub
        os.environ['GITHUB_TOKEN'] = token

        hubcmd = ['hub','pull-request',
                '-b','charlesreid1:master',
                '-h',branch_name,
                '-m',pr_msg]
        hubproc = subprocess.Popen(
                hubcmd,
                stdout=PIPE,
                stderr=PIPE,
                cwd=repo_dir
        )
        status_failed, status_file = record_and_check_output(hubproc,"create pull request",unique_filename)
        if status_failed:
            build_status = "fail"
            abort = True


    ######################
    # Clean up github token
    ######################

    os.environ['GITHUB_TOKEN'] = ""

    # end private-www submodule update PR 
    # -----------------------------------------------


    if not abort:
        logging.info("search demo submodule PR succeeded for submodule %s"%(full_repo_name))

    else:
        logging.info("search demo submodule PR failed for submodule %s"%(full_repo_name))

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



