import subprocess
import logging
from subprocess import PIPE
import tempfile
import json, os, re
from github import Github, GithubException
from datetime import datetime


"""
private-www Submodule Update PR for Uncle Archie


Description:

This is a bit of an odd "CI test" because it isn't exactly a CI test, but it is
part of a step-by-step CI workflow.

This hook listens for incoming push to master events from private-www
submodules.  When this type of event occurs, the hook opens an "update
private-www submodules" pull request.

(At that point, a new webhook is triggered and Uncle Archie will run a continuous
integration test on the newly-opened pull request.)


Installing webhoks:

Need to install a push to master webhook into each submodule.
"""

HTDOCS="/www/archie.nihdatacommons.us/htdocs"

def process_payload(payload, meta, config):
    """
    Look for any push events to the repositories 
    that are private-www submodules.

    When we get a push event, we should figure out
    whether it is on the master branch, and if so, 
    we open a new pull request that updates the submodules.

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
            'repo_whitelist' : ['dcppc/internal','dcppc/organize','dcppc/nih-demo-meetings','dcppc/dcppc-workshops'],
            'task_name' : 'Uncle Archie private-www Submodules Update PR',
            'pass_msg' : 'The private-www submodules update PR passed!',
            'fail_msg' : 'The private-www submodules update PR failed.',
    }


    repo_name = payload['repository']['name']
    full_repo_name = payload['repository']['full_name']

    sub_name = payload['repository']['name']
    full_sub_name = payload['repository']['full_name']


    # This must be a private-www submodule
    if full_repo_name not in params['repo_whitelist']:
        logging.debug("Skipping private-www submodule PR: this is not a whitelisted repo: %s"%(",".join(params['repo_whitelist'])))
        return

    # This must be a pull request
    if 'pull_request' not in payload.keys():
        logging.debug("Skipping private-www submodule PR: this is not a pull request")
        return

    if 'action' not in payload.keys():
        logging.debug("Skipping private-www submodule PR: this is not a pull request")
        return

    if payload['action']!='closed':
        logging.debug("Skipping private-www submodule PR: this pull request has not been closed yet")
        return

    # We want PRs that are being merged
    if 'merge_commit_sha' not in payload['pull_request']:
        logging.debug("Skipping private-www submodule PR: this pull request was not merged")
        return


    # -----------------------------------------------
    # Begin private-www submodule update PR 

    logging.info("Starting private-www submodule update pull request for %s"%(full_repo_name))



    unique = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_filename = "private_www_update_submodules_%s"%(unique)



    ######################
    # Make space.
    ######################

    scratch_dir = tempfile.mkdtemp()
    FNULL = open(os.devnull, 'w')


    ######################
    # Clone.
    ######################

    # Remember: you can only read() the output
    # of a PIPEd process once.

    abort = False

    parent_repo_name = "private-www"
    parent_full_repo_name = "dcppc/private-www"

    parent_branch_name = "master"

    # This is always the repo we clone
    parent_repo_url = "git@github.com:dcppc/%s"%(parent_repo_name)

    # get the API token
    token = config['github_access_token']

    # Note: this branch name (master) should be 
    # a parameter set by the user, so that they
    # can change it later.
    clonecmd = ['git','clone','--recursive','-b',parent_branch_name,parent_repo_url]
    logging.debug("Running cmd: %s"%(' '.join(clonecmd)))
    cloneproc = subprocess.Popen(
            clonecmd, 
            stdout=PIPE, 
            stderr=PIPE, 
            cwd=scratch_dir
    )
    status_failed, status_file = record_and_check_output(
            cloneproc,
            "git clone",
            unique_filename
    )
    ## Fails if word "error" or "exception" show up anywhere.
    #if status_failed:
    #    build_status = "fail"
    #    abort = True

    # We have two different workflows,
    # depending on whether a PR 
    # has already been opened or not
    token = config['github_access_token']
    g = Github(token)
    r = g.get_repo(full_repo_name)
    parent_r = g.get_repo(parent_full_repo_name)


    # Which commit are we updating the submodule to?
    # 
    # The merge_pr_event.json sample payload
    # includes this in the payload at
    # 
    #   payload['pull_request']['merge_commit_sha']
    # 
    new_sha = payload['pull_request']['merge_commit_sha']

    commit_prefix = '[Uncle Archie] Update submodule %s'%full_sub_name
    commit_msg = '%s to commit %s'%(commit_prefix,new_sha[0:7])
    pr_msg = commit_msg 


    # Iterate through all open pull requests having master as their base
    # Look for a PR containing commit_prefix in the title (updates same submodule)




    # 3 possibilities:
    # 1. If we find one PR with that in the title, use it (make our commit on that PR)
    # 2. If we find 2+ PRs with that in the title, keep the freshest, close the others
    # 3. No PRs, in which case, create branch and open PR



    # if there is an existing PR,
    # save the branch name 
    # and the pull request object
    existing_pr_head_sha = None
    existing_pr_head_branch = None
    existing_pr = None

    # is this the first open PR to update this submodule?
    first = True

    # Look for open PRs that update this submodule
    # (sort by most recent first)
    for pr in parent_r.get_pulls(state='open',sort='created',direction='desc',base='master'):

        # the pull request title should be prefixed with Uncle Archie
        # and include the name of the submodule being updated 
        if commit_prefix in pr.title:

            # We found an existing (stale) pull request that updates the submodule (to a stale commit)

            # Get head branch name for this existing pull request
            head_branch = payload['pull_request']['head']['ref']

            if first:
                # Save information about the existing pull request
                existing_pr_head_sha = pr.head.sha
                existing_pr_head_branch = pr.head.ref
                existing_pr = pr
                first = False
            else:
                # Close the (crusty) pull request
                pr.edit(state = 'closed')
            

    if existing_pr_head_sha is not None:

        # ------------------------------------
        # Begin "sync with existing PR" workflow 

        # We know that the existing PR
        # must be coming from a branch 
        # in this repo (not a fork)
        branch_name = existing_pr_head_branch


        # Update the PR title for this first (most recent) PR/commit
        # "[Uncle Archie] Update submodule dcppc/something to commit XYZ"
        pr.edit(title = commit_msg)



        ######################
        # Check out branch 
        ######################

        if not abort:

            repo_dir = os.path.join(scratch_dir, parent_repo_name)

            cocmd = ['git','checkout','-b',branch_name,'origin/%s'%(branch_name)]
            logging.debug("Running cmd: %s"%(' '.join(cocmd)))
            coproc = subprocess.Popen(
                    cocmd,
                    stdout=PIPE, 
                    stderr=PIPE, 
                    cwd=repo_dir
            )
            status_failed, status_file = record_and_check_output(
                    coproc,
                    "git checkout",
                    unique_filename
            )
            ## Fails if word "error" or "exception" show up anywhere.
            #if status_failed:
            #    build_status = "fail"
            #    abort = True

        # In case of new submodule
        if not abort:
            sucmd = ['git','submodule','update','--init']
            suproc = subprocess.Popen(
                    sucmd,
                    stdout=PIPE, 
                    stderr=PIPE, 
                    cwd=repo_dir
            )
            status_failed, status_file = record_and_check_output(
                    suproc,
                    "submodule update",
                    unique_filename
            )
            ## Fails if word "error" or "exception" show up anywhere.
            #if status_failed:
            #    build_status = "fail"
            #    abort = True
    
        ######################
        # Check out the master branch of the submodule
        # and pull the latest changes from upstream
        ######################
    
        if not abort:
    
            if repo_name == 'dcppc-workshops':
                submodule_dir_relative = os.path.join('docs','workshops')
            else:
                submodule_dir_relative = os.path.join('docs', repo_name)
    
            submodule_dir = os.path.join(repo_dir, submodule_dir_relative)
    


            subcocmd = ['git','checkout','master']
            logging.debug("Running cmd: %s"%(' '.join(subcocmd)))
            subcoproc = subprocess.Popen(
                    subcocmd,
                    stdout=PIPE, 
                    stderr=PIPE, 
                    cwd=submodule_dir
            )
            status_failed, status_file = record_and_check_output(
                    subcoproc,
                    "git checkout submodule",
                    unique_filename
            )
            ## Fails if word "error" or "exception" show up anywhere.
            #if status_failed:
            #    build_status = "fail"
            #    abort = True


    
            pullcmd = ['git','pull','origin','master']
            logging.debug("Running cmd: %s"%(' '.join(pullcmd)))
            pullproc = subprocess.Popen(
                    pullcmd,
                    stdout=PIPE, 
                    stderr=PIPE, 
                    cwd=submodule_dir
            )
            status_failed, status_file = record_and_check_output(
                    pullproc,
                    "git pull submodule",
                    unique_filename
            )
            ## Fails if word "error" or "exception" show up anywhere.
            #if status_failed:
            #    build_status = "fail"
            #    abort = True
    


        ######################
        # Add commit push the new submodule
        ######################
    
        if not abort:
    
            # Add the submodule
            addcmd = ['git','add',submodule_dir_relative]
            logging.debug("Running cmd: %s"%(' '.join(addcmd)))
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
            logging.debug("Running cmd: %s"%(' '.join(commitcmd)))
            commitproc = subprocess.Popen(
                    commitcmd,
                    stdout=PIPE,
                    stderr=PIPE,
                    cwd=repo_dir
            )
            status_failed, status_file = record_and_check_output(
                    commitproc,
                    "git commit submodule",
                    unique_filename
            )
            if status_failed:
                build_status = "fail"
                abort = True
    
    
    
            pushcmd = ['git','push','origin',branch_name]
            logging.debug("Running cmd: %s"%(' '.join(pushcmd)))
            pushproc = subprocess.Popen(
                    pushcmd,
                    stdout=PIPE,
                    stderr=PIPE,
                    cwd=repo_dir
            )
            status_failed, status_file = record_and_check_output(
                    pushproc,
                    "git push origin branch",
                    unique_filename
            )
            if status_failed:
                build_status = "fail"
                abort = True
    
        # End "sync with existing PR" workflow 
        # ------------------------------------

    else:

        # ------------------------------------
        # Begin "open new PR" workflow


        ######################
        # Unique branch name
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
            logging.debug("Running cmd: %s"%(' '.join(cocmd)))
            coproc = subprocess.Popen(
                    cocmd,
                    stdout=PIPE,
                    stderr=PIPE,
                    cwd=repo_dir
            )
            status_failed, status_file = record_and_check_output(
                    coproc,
                    "git checkout",
                    unique_filename
            )
            ## Fails if word "error" or "exception" show up anywhere.
            #if status_failed:
            #    build_status = "fail"
            #    abort = True

        # In case of new submodule
        if not abort:
            sucmd = ['git','submodule','update','--init']
            suproc = subprocess.Popen(
                    sucmd,
                    stdout=PIPE,
                    stderr=PIPE,
                    cwd=repo_dir
            )
            status_failed, status_file = record_and_check_output(
                    suproc,
                    "submodule update",
                    unique_filename
            )
            ## Fails if word "error" or "exception" show up anywhere.
            #if status_failed:
            #    build_status = "fail"
            #    abort = True


        ######################
        # Check out the master branch of the submodule
        # and pull the latest changes from upstream
        ######################

        if not abort:

            if repo_name == 'dcppc-workshops':
                submodule_dir_relative = os.path.join('docs','workshops')
            else:
                submodule_dir_relative = os.path.join('docs', repo_name)

            submodule_dir = os.path.join(repo_dir, submodule_dir_relative)

            subcocmd = ['git','checkout','master']
            logging.debug("Running cmd: %s"%(' '.join(subcocmd)))
            subcoproc = subprocess.Popen(
                    subcocmd,
                    stdout=PIPE,
                    stderr=PIPE,
                    cwd=submodule_dir
            )
            status_failed, status_file = record_and_check_output(
                    subcoproc,
                    "git checkout submodule",
                    unique_filename
            )
            ## Fails if word "error" or "exception" show up anywhere.
            #if status_failed:
            #    build_status = "fail"
            #    abort = True

            pullcmd = ['git','pull','origin','master']
            logging.debug("Running cmd: %s"%(' '.join(pullcmd)))
            pullproc = subprocess.Popen(
                    pullcmd,
                    stdout=PIPE,
                    stderr=PIPE,
                    cwd=submodule_dir
            )
            status_failed, status_file = record_and_check_output(
                    pullproc,
                    "git pull submodule",
                    unique_filename
            )
            ## Fails if word "error" or "exception" show up anywhere.
            #if status_failed:
            #    build_status = "fail"
            #    abort = True


        ######################
        # Add commit push the new submodule
        ######################

        if not abort:

            # Add the submodule
            addcmd = ['git','add',submodule_dir_relative]
            logging.debug("Running cmd: %s"%(' '.join(addcmd)))
            addproc = subprocess.Popen(
                    addcmd,
                    stdout=PIPE,
                    stderr=PIPE,
                    cwd=repo_dir
            )
            status_failed, status_file = record_and_check_output(
                    addproc,
                    "git add submodule",
                    unique_filename
            )
            if status_failed:
                build_status = "fail"
                abort = True


            # Commit the new submodule

            commitcmd = ['git','commit',submodule_dir_relative,'-m',commit_msg]
            logging.debug("Running cmd: %s"%(' '.join(commitcmd)))
            commitproc = subprocess.Popen(
                    commitcmd,
                    stdout=PIPE,
                    stderr=PIPE,
                    cwd=repo_dir
            )
            status_failed, status_file = record_and_check_output(
                    commitproc,
                    "git commit submodule",
                    unique_filename
            )
            if status_failed:
                build_status = "fail"
                abort = True



            pushcmd = ['git','push','origin',branch_name]
            logging.debug("Running cmd: %s"%(' '.join(pushcmd)))
            pushproc = subprocess.Popen(
                    pushcmd,
                    stdout=PIPE,
                    stderr=PIPE,
                    cwd=repo_dir
            )
            status_failed, status_file = record_and_check_output(
                    pushproc,
                    "git push origin branch",
                    unique_filename
            )
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
                    '-b','dcppc:master',
                    '-h',branch_name,
                    '-m',pr_msg]
            logging.debug("Running cmd: %s"%(' '.join(hubcmd)))
            hubproc = subprocess.Popen(
                    hubcmd,
                    stdout=PIPE,
                    stderr=PIPE,
                    cwd=repo_dir
            )
            status_failed, status_file = record_and_check_output(
                    hubproc,
                    "create pull request"
                    ,unique_filename
            )
            if status_failed:
                build_status = "fail"
                abort = True


        ######################
        # Clean up github token
        ######################

        os.environ['GITHUB_TOKEN'] = ""


        # End open new PR workflow
        # ------------------------------------


    # End private-www submodule update
    # -----------------------------------------------


    if not abort:
        logging.info("private-www submodule PR succeeded for submodule %s"%(full_repo_name))

    else:
        logging.info("private-www submodule PR failed for submodule %s"%(full_repo_name))

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



