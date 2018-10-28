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

OUTPUT_LOG="output/log"
OUTPUT_SERVE="output/serve"

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

            'build_task_name' : 'Uncle Archie private-www Integration Test',
            'build_pass_msg' : 'The private-www integration test passed!',
            'build_fail_msg' : 'The private-www integration test failed.',

            'serve_task_name' : 'Uncle Archie private-www Site Hosting',
            'serve_pass_msg' : 'The site is served!',
            'serve_fail_msg' : 'The site could not be served.',
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


    unique = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_filename = "private_www_integration_test_%s.txt"%(unique)
    unique_serve    = "private_www_integration_test_%s_serve"%(unique)

    status_url_log = "https://archie.nihdatacommons.us/output/log/%s"%(unique_filename)
    status_url_www = "https://archie.nihdatacommons.us/output/serve/%s"%(unique_serve)


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
        # triggered this test.

        # Get the head commit of the PR that
        # triggered this test, and update the
        # appropriate submodule before running
        # snakemake build_docs

        # Assemble submodule directory by 
        # determining which submodule was 
        # updated. that info is in the 
        # payload (repo_name)
        repo_dir = os.path.join(scratch_dir, "private-www")

        # Submodule remap:
        # {'dcppc-workshops':'workshops'}
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

        # Here.... we need to adjust mkdocs.yml 
        # set the site_url variable to the output/serve url
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

    if not abort:
        serve_dir = serve_htdocs_output(repo_dir,unique_serve)

    # end mkdocs build
    # -----------------------------------------------


    if build_status == "pass":

        if build_msg == "":
            build_msg = params['build_pass_msg']
        if serve_msg == "":
            serve_msg = params['serve_pass_msg']

        # build task status 
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


        logging.info("private-www integration test success:")
        logging.info("    Commit %s"%head_commit)
        logging.info("    PR %s"%pull_number)
        logging.info("    Repo %s"%full_repo_name)
        logging.info("    Output Log Link %s"%status_url_log)
        logging.info("    Serve Link %s"%status_url_www)
        return

    elif build_status == "fail":

        if build_msg == "":
            build_msg = params['fail_msg']
        if serve_msg == "":
            serve_msg = params['serve_fail_msg']

        try:
            commit_status = c.create_status(
                            state = "failure",
                            target_url = status_url_log,
                            description = build_msg,
                            context = params['build_task_name']
            )
        except GithubException as e:
            logging.exception("Github error: commit status failed to update.")

        logging.info("private-www integration test failure:")
        logging.info("    Commit %s"%head_commit)
        logging.info("    PR %s"%pull_number)
        logging.info("    Repo %s"%full_repo_name)
        logging.info("    Output Log Link %s"%status_url_log)
        return


def serve_htdocs_output(cwd_dir,unique_serve):
    """
    Given a folder name unique_htdocs containing
    the htdocs directory from this mkdocs run,
    """
    output_path = os.path.join(HTDOCS,OUTPUT_SERVE)
    output_file = os.path.join(output_path,unique_serve)

    if not os.path.exists(output_path):
        subprocess.call(['mkdir','-p',output_path])

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

    if not os.path.exists(output_path):
        logging.info('Creating output log path: %s'%(output_path))
        subprocess.call(['mkdir','-p',output_path])

    out = proc.stdout.read().decode('utf-8')
    err = proc.stderr.read().decode('utf-8')

    lout = out.lower()
    lerr = err.lower()

    lines = [ "================================\n",
              "========= STDOUT \n",
              "========= %s\n"%(" ".join(proc.args)),
              "\n\n",
              "======================\n",
              "========= STDERR \n",
              "========= %s\n"%(" ".join(proc.args)),
              err,
              "\n\n"]

    with open(output_file,'w') as f:
        [f.write(j) for j in lines]

    logging.info("Results from process: %s"%(label))
    logging.info("Running command: %s"%(" ".join(proc.args)))
    logging.info("%s"%(out))
    logging.info("%s"%(err))
    logging.info("Recorded in file: %s"%(output_file))

    if "exception" in lout or "exception" in lerr:
        return True, unique_filename

    if "error" in lout or "error" in lerr:
        return True, unique_filename

    return False, unique_filename

