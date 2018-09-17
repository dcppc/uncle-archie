from .base import UncleArchieTask
import logging
import pprint

class GithubTask(UncleArchieTask):
    """
    Base class for a Github test.
    """
    def __init__(self,config,**kwargs):
        """
        This performs the initialization procedure
        for Github-related Uncle Archie tasks.

        Remember, we run every Task with every payload,
        so Task.run() is where we validate the payload 
        to ensure we should be running that Task.

        config vars:
            repo_whitelist :        (list) whitelisted Github repositories
        """
        super().__init__(config,**kwargs)

        msg = "GithubTask: __init__(): Starting constructor"
        logging.debug(msg)

        self.get_api_key(config)

        # Get the API token when you actually need it, which
        # is to say, in the run() function, which has the config
        # variable avaiable. 
        self.token = None


    def get_api_key(self,config):
        """
        Get the API key for the Github API instance
        """
        if 'GITHUB_ACCESS_TOKEN' in config:
            self.token = config['GITHUB_ACCESS_TOKEN']
        else:
            err = "ERROR: GithubTask: __init__(): 'GITHUB_ACCESS_TOKEN' config variable: "
            err += "No Github API access token defined with 'GITHUB_ACCESS_TOKEN'"
            logging.error(err)
            logging.error("Config keys: %s"%(", ".join(config.keys())))
            raise Exception(err)

        msg = "  - Github API key: (FOUND) (hidden)"
        logging.debug(msg)


    def get_api_instance(self):
        """
        Return a Github API instance (PyGithub object)
            github_access_token :   (string) API access token
        """
        if self.token is None:
            err = "ERROR: GithubTask: get_api_instance(): This method was "
            err += "called before an API key was available via self.token\n"
            err += "You are likely missing a call to GithubTask.get_api_key()"
        else:
            g = Github(self.token)
            return g


    #######################################
    # Github payload info extraction 


    def get_clone_url(self,payload):
        """
        String: get a clone-able Github URL 
        for the repository in this payload
        (Tested)
        """
        if 'repository' in payload.keys():
            if 'clone_url' in payload['repository'].keys():
                return payload['repository']['clone_url']
        return None


    def get_ssh_url(self,payload):
        """
        String: get a clone-able SSH Github URL 
        for the repository in this payload
        (Tested)
        """
        if 'repository' in payload.keys():
            if 'ssh_url' in payload['repository'].keys():
                return payload['repository']['ssh_url']
        return None


    def get_html_url(self,payload):
        """
        String: get an HTML url to the Github repo
        for the repository in this payload
        (Tested)
        """
        if 'repository' in payload.keys():
            if 'html_url' in payload['repository'].keys():
                return payload['repository']['html_url']
        return None


    def get_full_repo_name(self,payload):
        """
        String: full repo name: organization/reponame
        (Tested)
        """
        if 'repository' in payload.keys():
            if 'full_name' in payload['repository'].keys():
                return payload['repository']['full_name']
        return None


    def get_short_repo_name(self,payload):
        """
        String: short repo name
        (Tested)
        """
        if 'repository' in payload.keys():
            if 'name' in payload['repository'].keys():
                return payload['repository']['name']
        return None


    def get_pull_request_head_commit(self,payload):
        """
        String: head commit of this pull request
        (Tested)
        """
        if self.is_pull_request(payload):
            return payload['pull_request']['head']['sha']
        return None


    def get_pull_request_number(self,payload):
        """
        String: get id number of pull request
        (Tested)
        """
        if self.is_pull_request(payload):
            return payload['number']
        return None


    def is_pull_request(self,payload):
        """
        Boolean: is this webhook a PR?
        (Tested)
        """
        if 'pull_request' in payload.keys():
            return True
        return False


    def is_pull_request_open(self,payload):
        """
        Boolean: is this webhook opening a PR?
        (Tested)
        """
        if 'action' in payload.keys():
            if payload['action']=='opened':
                return True
        return False


    def is_pull_request_sync(self,payload):
        """
        Boolean: is this webhook syncing a PR?
        (Tested)
        """
        if 'action' in payload.keys():
            if payload['action']=='synchronize':
                return True
        return False


    def is_pull_request_close(self,payload):
        """
        Boolean: is this webhook closing a PR?
        (Tested)
        """
        if 'action' in payload.keys():
            if payload['action']=='closed':
                return True
        return False


    def is_pull_request_merge_commit(self,payload):
        """
        Boolean: does this webhook have a PR merge commit?
        (Tested)
        """
        if self.is_pull_request(payload):
            if 'merge_commit_sha' in payload['pull_request']:
                return True
        return False


    def set_commit_status(
            self,
            full_repo_name,
            head_commit,
            state,
            build_msg,
            task_name,
            url = None
    ):
        """
        Set the commit status to (state)
        with description (description)
        and context (context)
        """
        g = self.get_api_instance()
        r = g.get_repo(full_repo_name)
        c = r.get_commit(head_commit)

        try:
            commit_status = c.create_status(
                            state = state,
                            target_url = url,
                            description = build_msg,
                            context = task_name
            )
        except GithubException as e:
            logging.info("ERROR: Github API: Set commit status for %s failed to update."%(head_commit))



"""
Uncle Archie PyGihub Task

This base class defines methods
for running a Python task with
Uncle Archie, namely, setting up
a virtual environment and wrapping
calls to python tools (e.g., mkdocs
and snakemake) to use the virtualenv
versions.

This functionality extends Github
tasks, rather than vice-versa, b/c
we may want to run Github tasks using
something other than Python.

(Example: docker-compose tests)

If we need to get the python functionality
without Github, we can just define a new 
class.
"""

class PyGithubTask(UncleArchieTask):
    """
    Base class for a Python + Github test.
    """
    def __init__(self,config,**kwargs):
        """
        This performs the initialization procedure
        common to all Uncle Archie tests that use
        Python in their task.

        config vars:
            vp_label :  What to call the virtual environment
            vp_dir :    (cwd = curr. working dir) the location 
                        of the virtual environment
        """
        super().__init__(config,**kwargs)

        VENV_LABEL = 'vp'

        # Get virtual environment label 
        # from config or use default
        if 'VENV_LABEL' in config.keys():
            self.venv_label = config['VENV_LABEL']
        else:
            self.venv_label = VENV_LABEL

        msg = "PyGithubTask: __init__(): New virtual environment will be named \"%s\""%(self.venv_label)
        logging.debug(msg)

    # NOTE:
    # We need to add a run_python method
    # that tacks on the venv path in front
    # of any binary that's passed 
    # (use with mkdocs, pelican, pip, python, etc.)


    def virtualenv_setup(self,**kwargs):
        """
        Set up a virtual environment.
        This is called once per task,
        right before Python commands are 
        run by the task.
        """
        if self.temp_dir is None:
            err = "ERROR: PyGithubTask: virtualenv_setup(): "
            err += "No temporary directory has been created yet!"
            logging.error(err)
            raise Exception(err)
        else:
            self.venv_dir = self.temp_dir

        msg = "PyGithubTask: virtualenv_setup(): Creating new virtual environment named \"%s\" "%(self.venv_label)
        msg += "in directory %s"%(self.venv_dir)
        logging.debug(msg)

        # Create the virtual environment
        subprocess.call(['virtualenv',self.venv_label],cwd=self.vp_dir)

        msg = "PyGithubTask: virtualenv_setup(): Success!"
        logging.debug(msg)


    def virtualenv_teardown(self,**kwargs):
        """
        Tear down a virtual environment.
        Called by the destructor.
        
        config vars:
            None
        """
        msg = "PyGithubTask: virtualenv_teardown(): Removing virtual environment at \"%s\" "%(self.vp_dir)
        logging.debug(msg)

        # Run the command ourselves, no logging needed
        subprocess.call(['rm','-fr',self.vp_dir])

        msg = "PyGithubTask: virtualenv_setup(): Success!"
        logging.debug(msg)

