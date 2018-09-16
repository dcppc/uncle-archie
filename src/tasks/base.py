import tempfile
import subprocess
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

    def __init__(self,config,**kwargs):
        """
        Extract parameters common to all tasks from the Flask config:
            log_dir:        Directory where logs for this task are stored
            htdocs_dir:     Directory where hosted web content goes
            base_url:       URL where hosted web content is available

        Parameters specific to tasks (extracted in methods defined
        here, but called from derived classes when we know the 
        task's label):
            name            Name of this task
            repo_whitelist  Whitelist of repositories to run this task on
        """
        msg = "UncleArchieTask: __init__(): Starting constructor"
        logging.debug(msg)

        # Get the log dir
        self.get_log_dir(config)

        # Get the htdocs dir
        self.get_htdocs_dir(config)

        # Get the base url
        self.get_base_url(config)

        # Get the value of the debug variable
        self.get_debug(config)

        # The following require a LABEL
        # to be defined by the parent class.
        if self.LABEL is None:
            err = "ERROR: UncleArchieTask: __init__(): Tried to extract "
            err += "test-specific config parametrers, but failed because "
            err += "no LABEL was defined for this test!"
            raise Exception(err)

        # Get the name of this task, using self.LABEL as default
        self.get_name(config,self.LABEL)

        # Get the repo whitelist for this task
        self.get_repo_whitelist(config,self.LABEL)

        msg = "UncleArchieTask: __init__(): Success!"
        logging.debug(msg)


    ######################################
    # Get config functions


    def get_log_dir(self,config):
        """
        Get the log directory from the Flask
        config, and create it if needed.
        """
        if 'log_dir' in config.keys():
            self.log_dir = config['log_dir']
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


    def get_htdocs_dir(self,config):
        """
        Get the htdocs directory from the Flask
        config, and check that it exists
        """
        if 'htdocs_dir' in config.keys():
            self.htdocs_dir = config['htdocs_dir']
        else:
            self.htdocs_dir = DEFAULT_HTDOCS_DIR

        # If it doesn't exist, make it
        if not os.path.isdir(self.log_dir):
            err = "ERROR: UncleArchieTask: get_htdocs_dir(): htdocs_dir kwarg: "
            err += "Could not find htdocs dir %s"%(self.htdocs_dir)
            logging.error(err)
            raise Exception(err)

        msg = "  - Htdocs dir: %s"%(self.htdocs_dir)
        logging.debug(msg)


    def get_base_url(self,config):
        """
        Get the base url from the Flask config
        """
        if 'base_url' in config.keys():
            self.base_url = config['base_url']
        else:
            self.base_url = DEFAULT_BASE_URL

        msg = "  - Base url: %s"%(self.base_url)
        logging.debug(msg)


    def get_debug(self,config):
        """
        Get a boolean indicating whether 
        Uncle Archie is running in debug
        mode (default: no)
        """
        self.debug = False
        if 'debug' in config.keys():
            if config['debug'] is True:
                self.debug = True


    def get_name(self,config,task_label):
        """
        Use the task label to get the task name.
        If the user has not specified one in the 
        config file, use the task label by default.
        """
        self.name = None
        if task_label in config.keys():
            if 'name' in config[task_label].keys():
                self.name = config[task_label]['name']

        if self.name==None:
            self.name = task_label

        msg = "  - Task name: %s"%(self.name)
        logging.debug(msg)


    def get_repo_whitelist(self,config,task_label):
        """
        Use the task label to get the repo whitelist.
        This is the list of repos to run this Task on.
        If the user has not specified any, set it to
        an empty list.
        """
        self.repo_whitelist = []
        if task_label in config.keys():
            if 'repo_whitelist' in config[task_label].keys():
                self.repo_whitelist = config[task_label]['repo_whitelist']

                # listify
                if type(self.repo_whitelist)==type(""):
                    self.repo_whitelist = [self.repo_whitelist]

        msg = "  - Repo whitelist: %s"%(", ".join(self.repo_whitelist))
        logging.debug(msg)


    ######################################
    # Passive run() function


    def run(self,payload,meta,config):
        """
        This does not perform ANY actions,
        it only sets up variables that will
        probably be used by all tasks.
        """
        self.dt = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # We have a unique datetime stamp for this payload
        # Use it to assemble an output file name

        # Name of log file unique to this test
        out_name = make_unique_label("output")
        self.log_file = os.path.join(self.log_dir,out_name)

        # Lists of strings to accumulate stdout and stderr
        self.log = [] 

        # No temporary directory
        # created here, that's up
        # to the task. See the
        # make_temp_dir() method
        # defined below.
        # 
        # (This is b/c tempfile
        #  module lets you create
        #  temp folders, but not
        #  create a temp folder name
        #  only. Stupid.)


    def make_temp_dir(self):
        """
        Creates a temporary dir with
        a unique name just for this
        task.

        Returns a string with the
        path to the temporary dir.

        Called by child classes.
        """
        self.temp_dir = tempfile.mkdtemp()
        return scratch_dir


    def rm_temp_dir(self):
        """
        Creates a temporary dir with
        a unique name just for this
        task.

        Returns a string with the
        path to the temporary dir.

        Called by child classes.
        """
        subprocess.call(['rm','-fr',self.temp_dir])


    ######################################
    # Function to run a command 
    # and log stdout/stderr to 
    # a log file


    def run_cmd(self, cmd, descr, cwd, **kwargs):
        """
        This runs the given command (cmd) 
        from the given directory (cwd) using 
        subprocess.

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
        if type(cmd)!=type([]):
            err = "ERROR: UncleArchieTask: run_cmd(): "
            err += "You must pass the command to run as a list, "
            err += "you passed a command of type %s"%(type(cmd))
            logging.error(err)
            raise Exception(err)

        if self.log is None:
            err = "ERROR: UncleArchieTask: run_cmd(): "
            err += "There was a problem with the output/error log accumulator (missing/none)"
            logging.error(err)
            raise Exception(err)

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
                  "======= CMD: %s\n"%(" ".join(cmd)),
                  "======= STDOUT\n",
                  "=====================================\n",
                  o,
                  "\n\n"
        ]

        elines = ["=====================================\n",
                  "======= CMD: %s\n"%(" ".join(cmd)),
                  "======= STDERR\n",
                  "=====================================\n",
                  e,
                  "\n\n"
        ]

        self.log += olines
        self.log += elines

        msg = "UncleArchieTask: run_cmd(): Finished running command"
        logging.debug(msg)

        if "exception" in o.lower \
        or "exception" in e.lower:
            err = " [X] ERROR: UncleArchieTask: run_cmd(): Detected exception [X]"
            logging.error(err)
            return True

        if "error" in o.lower \
        or "error" in e.lower:
            err = " [X] ERROR: UncleArchieTask: run_cmd(): Detected error [X]"
            logging.error(err)
            return True

        return False


    ######################################
    # More utility functions


    def make_unique_label(self, label):
        """
        Given a label, make it unique with self.dt.
        Useful for getting consistent filenames
        for output files.
        """
        assert label!=None
        return "%s_%s"%(label,dt)


    def save_payload(self,payload):
        """
        Save the webhook payload to a file
        """
        with open(self.payload_log,'w') as f:
            f.write(json.dumps(payload, indent=4))
        msg = "UncleArchieTask: save_payload(): Finished saving payload to file %s"%(self.payload_log)
        logging.debug(msg)


