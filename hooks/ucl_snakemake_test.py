import json, os, re
from github import Github, GithubException

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

    if payload['action'] not in ['opened','synchronize']:
        # we are only interested in PRs that are
        # being opened or updated
        return

    # This must be a whitelisted repo
    repo_name = payload['repository']['name']
    full_repo_name = payload['repository']['full_name']
    if full_repo_name not in params['repo_whitelist']:
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
    if check_for_errors(cloneproc,"git clone"):
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
        if check_for_errors(buildproc,"snakemake build"):
            build_status = "fail"
            abort = True
        else:
            # the only test that mattered, passed
            build_status = "pass"

    # end snakemake build
    # -----------------------------------------------

    if build_status == "pass":

        if build_msg == "":
            build_msg = params['pass_msg']

        try:
            commit_status = c.create_status(
                            state = "success",
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

def check_for_errors(proc,label):
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


