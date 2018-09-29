import subprocess
import logging
from subprocess import PIPE
import tempfile
import json, os, re
from github import Github, GithubException
from datetime import datetime

"""
private-www Build Test CI Hook for Uncle Archie

This hook should be installed in the private-www repository.
This will use snakemake to attempt to build the site.

If the build succeeds, the commit is marked as having succeed.
Otherwise the commit is marked as failed.
"""

HTDOCS="/www/archie.nihdatacommons.us/htdocs"

OUTPUT_LOGS="output/logs"
OUTPUT_HTDOCS="output/htdocs"

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
            'repo_whitelist' : ['dcppc/private-www'],

            'build_task_name' : 'Uncle Archie private-www Build Test',
            'build_pass_msg' : 'The private-www build test passed!',
            'build_fail_msg' : 'The private-www build test failed.',

            'htdocs_task_name' : 'Uncle Archie private-www Htdocs Serve',
            'htdocs_pass_msg' : 'The private-www htdocs are served!',
            'htdocs_fail_msg' : 'The private-www htdocs could not be served.',
    }

    # This must be a pull request
    if ('pull_request' not in payload.keys()) or ('action' not in payload.keys()):
        return

    # This must be a whitelisted repo
    repo_name = payload['repository']['name']
    full_repo_name = payload['repository']['full_name']
    if full_repo_name not in params['repo_whitelist']:
        logging.debug("Skipping private-www build test: this is not the private-www repo")
        return

    # We are only interested in PRs that are
    # being opened or updated
    if payload['action'] not in ['opened','synchronize']:
        logging.debug("Skipping private-www build test: this is not opening/updating a PR")
        return

    if payload['pull_request']['base']['ref']=='heroku-pages':
        logging.debug("Skipping private-www build test because PR is based on heroku-pages branch")
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

    gitc = c.commit
    commit_message = gitc.message

    # -----------------------------------------------
    # start private-www build test with snakemake

    logging.info("Starting private-www build test build for submodule %s"%(full_repo_name))

    # Strategy:
    # * This will _always_ use private-www  as the build repo
    # * This will _always_ clone recursively
    # * This will _only_ update the submodule of interest,
    #   to the head commit of the pull request.
    # * This will run mkdocs on the entire private-www site.


    unique = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_filename = "private_www_build_test_%s"%(unique)
    unique_htdocs   = "private_www_build_test_%s_htdocs"%(unique)

    status_url_log = "https://archie.nihdatacommons.us/output/log/%s"%(status_file)
    status_url_www = "https://archie.nihdatacommons.us/output/htdocs/%s"%(htdocs_dir)


    ######################
    # logic. noise.
    ######################

    # Build: fail by default!
    build_status = "fail"
    build_msg = "" # if blank at the end, use the default

    # Serving htdocs: fail by default!
    htdocs_status = "fail"
    htdocs_msg = ""


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
    status_failed, status_file = record_and_check_output(
            cloneproc,
            "git clone",
            unique_filename,
            ignore_text=commit_message
    )
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
        status_failed, status_file = record_and_check_output(
                coproc,
                "git checkout",
                unique_filename,
                ignore_text=commit_message
        )
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
        status_failed, status_file = record_and_check_output(
                suproc,
                "submodule update",
                unique_filename,
                ignore_text=commit_message
        )
        if status_failed:
            build_status = "fail"
            abort = True

    if not abort:

        # Here.... we need to adjust mkdocs.yml 
        # set the site_url variable to the output/htdocs url
        # that way the test site will interlink

        mkdocs_pre = []
        mkdocs_dot_yml = os.path.join(repo_dir,'mkdocs.yml')

        with open(mkdocs_dot_yml,'r') as f:
            mkdocs_pre = f.readlines()

        mkdocs_post = []
        for line in mkdocs_pre:
            if 'site_url' in line:
                mkdocs_post.append("site_url: %s"%(status_url_www))
            else:
                mkdocs_post.append(line)

        with open(mkdocs_dot_yml,'w') as f:
            f.write("\n".join(mkdocs_post))


    if not abort:
        buildcmd = ['snakemake','--nocolor','build_docs']
        buildproc = subprocess.Popen(
                buildcmd, 
                stdout=PIPE,
                stderr=PIPE, 
                cwd=repo_dir
        )
        status_failed, status_file = record_and_check_output(
                buildproc,
                "snakemake build",
                unique_filename,
                ignore_text=commit_message
        )
        if status_failed:
            build_status = "fail"
        else:
            # the only test that mattered, passed
            build_status = "pass"

    if not abort:
        htdocs_dir = serve_htdocs_output(repo_dir,unique_htdocs)
        
    # end snakemake build
    # -----------------------------------------------


    
    if build_status == "pass":

        if build_msg == "":
            build_msg = params['build_pass_msg']
        if htdocs_msg == "":
            htdocs_msg = params['htdocs_pass_msg']

        # build task status 
        try:
            commit_status = c.create_status(
                            state = "success",
                            target_url = status_url_log,
                            description = build_msg,
                            context = params['build_task_name']
            )
        except GithubException as e:
            logging.info("Github error: commit status failed to update.")

        # htdocs hosting task status 
        try:
            commit_status = c.create_status(
                            state = "success",
                            target_url = status_url_www,
                            description = htdocs_msg,
                            context = params['htdocs_task_name']
            )
        except GithubException as e:
            logging.info("Github error: commit status failed to update.")

        logging.info("private-www build test succes:")
        logging.info("    Commit %s"%head_commit)
        logging.info("    PR %s"%pull_number)
        logging.info("    Repo %s"%full_repo_name)
        logging.info("    Output Log Link %s"%status_url_log)
        logging.info("    Htdocs Serve Link %s"%status_url_www)
        return

    elif build_status == "fail":

        if build_msg == "":
            build_msg = params['build_fail_msg']
        if htdocs_msg == "":
            htdocs_msg = params['htdocs_pass_msg']

        try:
            commit_status = c.create_status(
                            state = "failure",
                            target_url = status_url,
                            description = build_msg,
                            context = params['build_task_name']
            )
        except GithubException as e:
            logging.info("Github error: commit status failed to update.")

        logging.info("private-www build test failure:")
        logging.info("    Commit %s"%head_commit)
        logging.info("    PR %s"%pull_number)
        logging.info("    Repo %s"%full_repo_name)
        logging.info("    Output Log Link %s"%status_url)
        return



def serve_htdocs_output(cwd_dir,unique_htdocs):
    """
    Given a folder name unique_htdocs containing
    the htdocs directory from this mkdocs run,
    """
    output_path = os.path.join(HTDOCS,OUTPUT_HTDOCS)
    output_file = os.path.join(output_path,unique_htdocs)

    if not os.path.exists(output_path):
        os.mkdir(output_path)

    try:
        subprocess.call(['mv','site',output_file],
                    cwd=cwd_dir)
    except:
        err = "Error moving site/ to %s"%(output_file)
        logging.error(err)
        raise Exception(err)

    return unique_htdocs



def record_and_check_output(proc,label,unique_filename,ignore_text=None):
    """
    Given a process, get the stdout and stderr streams
    and record them in an output file that can be provided
    to users as a link. 
    
    Run this function on the last/most important step
    in your CI test. 

    ignore_text is a string that should be stripped out of 
    the output to prevent it from accidentally triggering 
    the "error" or "exception" detector.

    Returns:

    status_failed       Boolean: did status fail?
    status_file         String: filename where log is located
    """ 
    output_path = os.path.join(HTDOCS,OUTPUT_LOGS)
    output_file = os.path.join(output_path,unique_filename)

    if not os.path.exists(output_path):
        os.mkdir(output_path)

    out = proc.stdout.read().decode('utf-8')
    err = proc.stderr.read().decode('utf-8')

    lout = out.lower()
    lerr = err.lower()

    # Strip out ignore_text
    if ignore_text is not None:
        lout = re.sub(ignore_text,'',lout)
        lerr = re.sub(ignore_text,'',lerr)


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


