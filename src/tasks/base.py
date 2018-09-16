import tempfile
import datetime
import logging


"""
Uncle Archie: Base Classes

The classes in this file are intended to be used
as base classes only. None of them define a 
process_payload() method, which is a virtual
method that must be defined by a Task class
to use that Task with Uncle Archie.
"""


class UncleArchieTask(object):
    """
    Abstract base class. Represents a task that
    Uncle Archie performs when a webhook is received.
    (Tasks are usually CI tests.)
    """
    DEFAULT_LOG_DIR = "/tmp/archie"
    DEFAULT_HTDOCS_DIR = "/www/archie.nihdatacommons.us/htdocs/output"
    DEFAULT_BASE_URL = "https://archie.nihdatacommons.us/output/"

    def __init__(self,**kwargs):
        """
        We don't do much in the Task initialization,
        except make placeholders for all the variables
        we will eventually set and use in process_payload(),
        when we actually have the Flask config

        parameters common to all tests:
            log_dir
            htdocs_dir
            base_url
        """
        logging.debug("UncleArchieTask: __init__(): Starting constructor")
        self.dt = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_dir    = None
        self.htdocs_dir = None
        self.base_url   = None
        logging.debug("UncleArchieTask: __init__(): Finishing constructor")


    def process_payload(self,payload,meta,config):
        """
        """
        err = "ERROR: UncleArchieTask: process_payload(): "
        err += "This is a virtual method and must be overridden "
        err += "by a child class."
        logging.error(err)
        raise Exception(err)


    def save_payload(self,payload):
        """
        Save the webhook payload to a file
        """
        with open(self.payload_log,'w') as f:
            f.write(json.dumps(payload, indent=4))
        msg = "UncleArchieTask: save_payload(): Finished saving payload to file %s"%(self.payload_log)
        logging.debug(msg)


    def make_unique_label(self, label):
        """
        Given a label, make it unique with self.dt.
        Useful for getting consistent filenames
        for output files.
        """
        assert label!=None
        return "%s_%s"%(label,dt)


    def run_cmd(self, cmd, descr, cwd, **kwargs):
        """
        Params:
            cmd :   (list) the command to run
            descr : (string) short description
            cwd :   (string) curr working dir

        kwargs:
            None

        Returns:
            abort : (boolean) did the process encounter
                    errors or exceptions
        """
        msg = "UncleArchieTask: run_cmd(): About to run command:\n"
        msg += "    %s\n"%(" ".join(cmd))
        logging.debug(msg)

        proc = subprocess.Popen(
                cmd,
                stdout=PIPE,
                stderr=PIPE,
                cwd=cwd
        )

        o = proc.stdout.read().decode('utf-8')
        e = proc.stderr.read().decode('utf-8')

        elines = ["=====================================\n",
                  "======= CMD: %s\n"%(" ".join(cmd))
                  "======= STDOUT\n",
                  "=====================================\n",
                  o,
                  "\n\n"
        ]

        elines = ["=====================================\n",
                  "======= CMD: %s\n"%(" ".join(cmd))
                  "======= STDERR\n",
                  "=====================================\n",
                  e,
                  "\n\n"
        ]

        self.out += olines
        self.err += elines

        msg = "UncleArchieTask: run_cmd(): Finished running command"
        logging.debug(msg)

        if "exception" in out.lower
        or "exception" in err.lower:
            err = " [X] ERROR: UncleArchieTask: run_cmd(): Detected exception [X]"
            logging.error(err)
            return True

        if "error" in out.lower
        or "error" in err.lower:
            err = " [X] ERROR: UncleArchieTask: run_cmd(): Detected error [X]"
            logging.error(err)
            return True

        return False



class GithubTask(UncleArchieTask):
    """
    Base class for a Github test.
    """
    def __init__(self,**kwargs):
        """
        This performs the initialization procedure
        for Github-related Uncle Archie tasks.

        Remember, we run every hook with every payload,
        so process_payload() is where we have to decide
        whether to run this test (i.e. check if the repo in
        this payload is on the whitelist).

        kwargs:
            github_access_token :   (string) API access token
            repo_whitelist :        (list) whitelisted Github repositories
        """
        # Get API key and save it
        if 'github_access_token' in kwargs:
            self.token = kwargs.pop('github_access_token')
        else:
            err = "ERROR: GithubTask: __init__(): kwarg github_access_token: "
            err += "No Github API access token defined with 'github_access_token' kwarg"
            logging.error(err)
            raise Exception(err)

        # Get repo whitelist and save it
        if 'repo_whitelist' in kwargs:
            self.repo_whitelist = kwargs.pop('repo_whitelist')
        else:
            err = "ERROR: GithubTask: __init__(): kwarg repo_whitelist: "
            err += "No Github whitelist defined with 'repo_whitelist' kwarg"
            logging.error(err)
            raise Exception(err)


    def get_api_instance(self):
        """
        Return a Github API instance (PyGithub object)
        """
        g = Github(self.token)
        return g


    def get_clone_url(self,payload):
        """
        String: get a clone-able Github URL 
        for the repository in this payload
        """
        if 'repository' in payloads.keys():
            if 'clone_url' in payload['repository'].keys():
                return payloads['repository']['clone_url']
        return None


    def get_ssh_url(self,payload):
        """
        String: get a clone-able SSH Github URL 
        for the repository in this payload
        """
        if 'repository' in payloads.keys():
            if 'ssh_url' in payload['repository'].keys():
                return payloads['repository']['ssh_url']
        return None


    def get_html_url(self,payload):
        """
        String: get an HTML url to the Github repo
        for the repository in this payload
        """
        if 'repository' in payloads.keys():
            if 'html_url' in payload['repository'].keys():
                return payloads['repository']['html_url']
        return None


    def get_full_repo_name(self,payload):
        """
        String: full repo name: organization/reponame
        """
        if 'repository' in payload.keys():
            if 'full_name' in payload['repository'].keys():
                return payload['repository']['full_name']
        return None


    def get_short_repo_name(self,payload):
        """
        String: short repo name
        """
        if 'repository' in payload.keys():
            if 'name' in payload['repository'].keys():
                return payload['repository']['name']
        return None


    def get_pull_request_head(self,payload):
        """
        String: head commit of this pull request
        """
        if self.is_pull_request(payload):
            return payload['pull_request']['head']['sha']
        return None


    def get_pull_request_number(self,payload):
        """
        String: get id number of pull request
        """
        if self.is_pull_request(payload):
            return payload['number']
        return None


    def is_pull_request(self,payload):
        """
        Boolean: is this webhook a PR?
        """
        if 'pull_request' in payload.keys():
            return True
        return False


    def is_pull_request_open(self,payload):
        """
        Boolean: is this webhook opening a PR?
        """
        if 'action' in payload.keys():
            if payload['action']=='opened':
                return True
        return False


    def is_pull_request_sync(self,payload):
        """
        Boolean: is this webhook syncing a PR?
        """
        if 'action' in payload.keys():
            if payload['action']=='synchronize':
                return True
        return False


    def is_pull_request_close(self,payload):
        """
        Boolean: is this webhook closing a PR?
        """
        if 'action' in payload.keys():
            if payload['action']=='closed':
                return True
        return False


    def is_pull_request_merge_commit(self,payload):
        """
        Boolean: does this webhook have a PR merge commit?
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
        g = self.get_api
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
    def __init__(self,**kwargs):
        """
        This performs the initialization procedure
        common to all Uncle Archie tests that use
        Python in their task.

        kwargs:
            vp_label :  What to call the virtual environment
            vp_dir :    (cwd = curr. working dir) the location 
                        of the virtual environment
        """
        super().__init__(**kwargs)
        self.setup_virtualenv(**kwargs)


    def __del__(self,**kwargs):
        """
        Destructor
        """
        msg = "PyGithubTask: __del__(): Tearing down virtual environment"
        logging.debug(msg)
        self.teardown_virtualenv(**kwargs)


    def setup_virtualenv(self,**kwargs):
        """
        Set up a virtual environment.
        Called by the constructor.

        kwargs:
            vp_label :  What to call the virtual environment
            vp_dir :    (cwd = curr. working dir) the location 
                        of the virtual environment
        """
        # Get the name of the virtual environment
        if 'vp_label' in kwargs:
            self.vp_label = kwargs.pop('vp_label')
        else:
            self.vp_label = 'vp'

        # Get the directory of the virtual environment
        if 'vp_dir' in kwargs:
            self.vp_dir = kwargs.pop('vp_dir')
        else:
            self.vp_dir = self.temp_dir

        msg = "PyGithubTask: setup_virtualenv(): Creating new virtual environment named \"%s\" "%(self.name)
        msg += "in location \"%s\""%(self.vp_dir)
        logging.debug(msg)

        # Create the virtual environment
        subprocess.call(['virtualenv',vp_label],cwd=self.vp_dir)

        msg = "PyGithubTask: setup_virtualenv(): Success!"
        logging.debug(msg)


    def teardown_virtualenv(self,**kwargs):
        """
        Tear down a virtual environment.
        Called by the destructor.
        
        kwargs:
            None
        """
        msg = "PyGithubTask: teardown_virtualenv(): Removing virtual environment at \"%s\" "%(self.vp_dir)
        logging.debug(msg)

        # Run the command ourselves, no logging needed
        subprocess.call(['rm','-fr',self.vp_dir])

        msg = "PyGithubTask: setup_virtualenv(): Success!"
        logging.debug(msg)

