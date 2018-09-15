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

Derived classes are in:
    simple_classes.py
    pr_classes.py
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
        This performs the initialization procedure
        common to all Uncle Archie tasks: 
         - get name
         - get temporary directory
         - get log dir/log file
         - get htdocs outupt directory
         - get htdocs output url 
         
        Remember that we run every hook with every payload,
        so process_payload() is where we decide whether to
        actually run tests.

        kwargs:
            name :          Print-friendly name of this task
            label :         Filename-friendly short label for this task
            temp_dir :      Directory where the mess will be made and then cleaned up
            log_dir :       Directory where output logs should go
            htdocs_dir :    Directory where web-hosted output goes
            base_url :      Base URL for content hosted at htdocs_dir
        """
        self.dt = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Get the name of the task
        if 'name' in kwargs:
            self.name = kwargs.pop('name')
        else:
            err = "ERROR: UncleArchieTask: __init__(): name kwarg: "
            err += "No name kwarg was provided to the constructor."
            logging.error(err)
            raise Exception(err)

        # Get the name of the task
        if 'label' in kwargs:
            self.label = kwargs.pop('label')
        else:
            err = "ERROR: UncleArchieTask: __init__(): label kwarg: "
            err += "No label kwarg was provided to the constructor."
            logging.error(err)
            raise Exception(err)

        msg = "UncleArchieTask: __init__(): Creating new Uncle Archie Task\n"
        msg += "Name: %s\n"%(self.name)
        msg += "Label: %s\n"%(self.label)
        logging.debug(msg)

        # Get the temporary directory
        if 'temp_dir' in kwargs:
            self.temp_dir = kwargs.pop('temp_dir')
        else:
            rand = hashlib.md5(self.dt.encode()).hexdigest()
            self.temp_dir = os.path.join('/tmp',rand)

        # If it doesn't exist, make it
        if not os.path.isdir(self.temp_dir):
            result = subprocess.call(['mkdir','-p',self.temp_dir])
            if result==1:
                err = "ERROR: UncleArchieTask: __init__(): temp_dir kwarg: "
                err += "Could not create temp dir %s"%(self.temp_dir)
                logging.error(err)
                raise Exception(err)

        msg = "  - Temporary dir: %s"%(self.temp_dir)
        logging.debug(msg)

        # Get the output log directory
        if 'log_dir' in kwargs:
            self.log_dir = kwargs.pop('log_dir')
        else:
            self.log_dir = DEFAULT_LOG_DIR

        # If it doesn't exist, make it
        if not os.path.isdir(self.log_dir):
            result = subprocess.call(['mkdir','-p',self.log_dir])
            if result==1:
                err = "ERROR: UncleArchieTask: __init__(): log_dir kwarg: "
                err += "Could not create log dir %s"%(self.log_dir)
                logging.error(err)
                raise Exception(err)

        msg = "  - Log dir: %s"%(self.log_dir)
        logging.debug(msg)

        # Get the htdocs directory
        if 'htdocs_dir' in kwargs:
            self.htdocs_dir = kwargs.pop('htdocs_dir')
        else:
            self.htdocs_dir = DEFAULT_HTDOCS_DIR

        # If it doesn't exist, throw a tantrum
        if not os.path.isdir(self.htdocs_dir):
            err = "ERROR: UncleArchieTask: __init__(): htdocs_dir kwarg: "
            err += "Specified htdocs directory \"%s\" "%(self.htdocs_dir)
            err += "does not exist."
            logging.error(err)
            raise Exception(err)

        msg = "  - Htdocs dir: %s"%(self.htdocs_dir)
        logging.debug(msg)

        # Get the base url
        if 'base_url' in kwargs:
            self.base_url = kwargs.pop('base_url')
        else:
            self.base_url = DEFAULT_BASE_URL

        msg = "  - Base url: %s"%(self.base_url)
        logging.debug(msg)

        # Make log file names - 
        # these log files are the ones
        # linked to in the final UA report.
        out_name = make_unique_label("stdout")
        self.out_log = os.path.join(self.log_dir,out_name)
        self.out = [] # list of strings

        err_name = make_unique_label("stderr")
        self.err_log = os.path.join(self.log_dir,err_name)
        self.err = [] # list of strings

        payload_name = make_unique_label("payload")
        self.payload_log = os.path.join(self.log_dir,payload_name)

        msg = "UncleArchieTask: __init__(): Log locations have been set:\n"
        msg += "  - Stdout log: %s\n"%(self.out_log)
        msg += "  - Stderr log: %s\n"%(self.err_log)
        msg += "  - Payload log: %s\n"%(self.payload_log)
        logging.debug(msg)

        msg = "UncleArchieTask: __init__(): Success!"
        logging.debug(msg)


    def make_unique_label(self, label):
        """
        Given a label, make it unique with self.dt.
        Useful for getting consistent filenames
        for output files.
        """
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


    def save_payload(self,payload):
        """
        Save the webhook payload to a file
        """
        with open(self.payload_log,'w') as f:
            f.write(json.dumps(payload, indent=4))
        msg = "UncleArchieTask: save_payload(): Finished saving payload to file %s"%(self.payload_log)
        logging.debug(msg)


    def process_payload(self,payload):
        """
        Virtual method: process the webhook payload
        """
        err = "ERROR: UncleArchieTask: process_payload(): "
        err += "This is a virtual method and must be overridden "
        err += "by a child class."
        logging.error(err)
        raise Exception(err)


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

