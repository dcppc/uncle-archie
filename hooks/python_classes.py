
"""
Uncle Archie Python Task

This base class defines methods
for running a Python task with
Uncle Archie, namely, setting up
a virtual environment and wrapping
calls to python tools (e.g., mkdocs
and snakemake) to use the virtualenv
versions.

This functionality extends Github
tasks, rather than vice-versa, b/c
the logic is that we may want to run
non-Python tests but still keep the
funtionality to get the head commit
of a pull request, check if merging,
mark commits as success, etc etc.

Example: docker-compose tests.
"""

class PythonTask(UncleArchieTask):
    """
    Base class for a Python test.
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
        msg = "PythonTask: __del__(): Tearing down virtual environment"
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

        msg = "PythonTask: setup_virtualenv(): Creating new virtual environment named \"%s\" "%(self.name)
        msg += "in location \"%s\""%(self.vp_dir)
        logging.debug(msg)

        # Create the virtual environment
        subprocess.call(['virtualenv',vp_label],cwd=self.vp_dir)

        msg = "PythonTask: setup_virtualenv(): Success!"
        logging.debug(msg)


    def teardown_virtualenv(self,**kwargs):
        """
        Tear down a virtual environment.
        Called by the destructor.
        
        kwargs:
            None
        """
        msg = "PythonTask: teardown_virtualenv(): Removing virtual environment at \"%s\" "%(self.vp_dir)
        logging.debug(msg)

        # Run the command ourselves, no logging needed
        subprocess.call(['rm','-fr',self.vp_dir])

        msg = "PythonTask: setup_virtualenv(): Success!"
        logging.debug(msg)

