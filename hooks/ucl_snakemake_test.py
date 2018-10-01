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

OUTPUT_LOG="output/log"
OUTPUT_SERVE="output/ucl"

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
            'repo_whitelist' : ['dcppc/use-case-library'],

            'build_task_name' : 'Uncle Archie Use Case Library Pull Request Tester',
            'build_pass_msg' : 'The use-case-library build test passed!',
            'build_fail_msg' : 'The use-case-library build test failed.',

            'serve_task_name' : 'Uncle Archie Use Case Library Site Hosting',
            'serve_pass_msg' : 'The site is served!',
            'serve_fail_msg' : 'The site could not be served.',
    }

    # This must be a pull request
    if ('pull_request' not in payload.keys()) or ('action' not in payload.keys()):
        logging.debug("Skipping use-case-library integration test: this is not a pull request")
        return

    # This must be the use-case-library repo
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

    if payload['pull_request']['base']['ref']=='gh-pages':
        logging.debug("Skipping use-case-library build test because PR is based on gh-pages branch")
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
    # start use-case-library build test with snakemake
    logging.info("Starting use-case-library build test build")

    unique = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_filename = "ucl_build_test_%s.txt"%(unique)
    unique_serve    = "ucl_build_test_%s_serve"%(unique)

    status_url_log = "https://archie.nihdatacommons.us/%s/%s"%(OUTPUT_LOG,unique_filename)
    status_url_www = "https://archie.nihdatacommons.us/%s/%s"%(OUTPUT_SERVE,unique_serve)


    ######################
    # logic. noise.
    ######################

    # Build: fail by default!
    build_status = "fail"
    build_msg = "" # if blank at the end, use the default

    # Serving: fail by default!
    serve_status = "fail"
    serve_msg = ""


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


    if not abort:

        # Adjust site_url in mkdocs.yml

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

        # Set up the virtual environment
        venv = ['virtualenv','vp']
        venvproc = subprocess.Popen(
                venv, 
                stdout=PIPE,
                stderr=PIPE, 
                cwd=repo_dir
        )
        status_failed, status_file = record_and_check_output(
                venvproc,
                "virtualenv vp",
                unique_filename,
                ignore_text=commit_message
        )
        if status_failed:
            build_status = "fail"
            abort = True


        # Install requirements.txt
        srcvenv = ['vp/bin/pip','install','-r','requirements.txt']
        srcvenvproc = subprocess.Popen(
                srcvenv, 
                stdout=PIPE,
                stderr=PIPE, 
                cwd=repo_dir
        )
        status_failed, status_file = record_and_check_output(
                srcvenvproc,
                "pip install",
                unique_filename,
                ignore_text=commit_message
        )
        if status_failed:
            build_status = "fail"
            abort = True



    if not abort:
        buildcmd = ['vp/bin/snakemake','--nocolor','build']
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
        serve_dir = serve_htdocs_output(repo_dir,unique_serve)

    # end snakemake build
    # -----------------------------------------------


    if build_status == "pass":

        if build_msg == "":
            build_msg = params['build_pass_msg']

        try:
            commit_status = c.create_status(
                            state = "success",
                            target_url = status_url_log,
                            description = build_msg,
                            context = params['build_task_name']
            )
        except GithubException as e:
            logging.exception("Github error: commit status failed to update.")

        # serve task status 
        try:
            commit_status = c.create_status(
                            state = "success",
                            target_url = status_url_www,
                            description = serve_msg,
                            context = params['serve_task_name']
            )
        except GithubException as e:
            logging.exception("Github error: commit status failed to update.")

        logging.info("use-case-library build test success:")
        logging.info("    Commit %s"%head_commit)
        logging.info("    PR %s"%pull_number)
        logging.info("    Repo %s"%full_repo_name)
        logging.info("    Output Log Link %s"%status_url_log)
        logging.info("    Serve Link %s"%status_url_www)
        return

    elif build_status == "fail":

        if build_msg == "":
            build_msg = params['build_fail_msg']
        if serve_msg == "":
            serve_msg = params['serve_fail_msg']

        try:
            commit_status = c.create_status(
                            state = "failure",
                            target_url = status_url,
                            description = build_msg,
                            context = params['build_task_name']
            )
        except GithubException as e:
            logging.exception("Github error: commit status failed to update.")

        logging.info("use-case-library build test failure:")
        logging.info("    Commit %s"%head_commit)
        logging.info("    PR %s"%pull_number)
        logging.info("    Repo %s"%full_repo_name)
        logging.info("    Output Log Link %s"%status_url)
        return



def serve_htdocs_output(cwd_dir,unique_serve):
    """
    Given a folder name unique_htdocs containing
    the htdocs directory from this mkdocs run,
    """
    output_path = os.path.join(HTDOCS,OUTPUT_SERVE)
    output_file = os.path.join(output_path,unique_serve)

    if not os.path.exists(output_path):
        os.mkdir(output_path)

    try:
        subprocess.call(
                ['mv','site/content',output_file],
                cwd=cwd_dir
        )
    except:
        err = "Error moving site/content/ to %s"%(output_file)
        logging.error(err)
        raise Exception(err)

    return unique_serve


def record_and_check_output(proc,label,unique_filename,ignore_text=None):
    """
    Given a process, get the stdout and stderr streams
    and record them in an output file that can be provided
    to users as a link. Also return a boolean on whether
    there was a problem with the process.

    Run this function on the last/most important step
    in your CI test. 

    ignore_text is a string that should be stripped out of 
    the output to prevent it from accidentally triggering 
    the "error" or "exception" detector.

    Returns:

    status_failed       Boolean: did status fail?
    status_file         String: filename where log is located
    """ 
    output_path = os.path.join(HTDOCS,OUTPUT_LOG)
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

