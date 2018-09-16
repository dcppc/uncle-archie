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

    def __init__(self,config,**kwargs):
        """
        Extract parameters common to all tasks from the Flask config:
            log_dir:        Directory where logs for this task are stored
            htdocs_dir:     Directory where hosted web content goes
            base_url:       URL where hosted web content is available
        """
        logging.debug("UncleArchieTask: __init__(): Starting constructor")

        # ---------------------------
        # Get the log dir
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

        # ---------------------------
        # Get the htdocs dir
        if 'htdocs_dir' in kwargs:
            self.htdocs_dir = config['htdocs_dir']
        else:
            self.htdocs_dir = DEFAULT_HTDOCS_DIR

        msg = "  - Htdocs dir: %s"%(self.htdocs_dir)
        logging.debug(msg)

        # ---------------------------
        # Get the base url
        if 'base_url' in kwargs:
            self.base_url = config['base_url']
        else:
            self.base_url = DEFAULT_BASE_URL

        msg = "  - Base url: %s"%(self.base_url)
        logging.debug(msg)

        msg = "UncleArchieTask: __init__(): Success!"
        logging.debug(msg)


    def process_payload(self,payload,meta,config):
        """
        Perform any actions common to all Tasks here
        """
        self.dt = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # We have a unique datetime stamp for this payload
        # Use it to assemble an output file name

        # Create a file to record logs:
        out_name = make_unique_label("output")
        self.log_file = os.path.join(self.log_dir,out_name)

        # Lists of strings to accumulate stdout and stderr
        self.log = [] 



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


