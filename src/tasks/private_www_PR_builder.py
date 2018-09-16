from .github_base import PyGithubTask

class private_www_PR_builder(PyGithubTask):
    # Once this is defined, the parent constructor
    # will be able to extract task-specific config
    # parameters for us. Nice!
    LABEL = "private_www_PR_builder"


    def run(self,payload,meta,config):
        """
        This is the main method that runs the task.
        """
        super().run(payload,meta,config)

        # Abort if not right kind of webhook
        if not self.validate(payload):
            return

        # We don't need to share info or pass lots of params.
        # Rather, each method is passed the payload and uses
        # this class's utility methods to get the info it needs.

        # Internal flag used to stop on errors
        self.abort = False

        self.make_temp_dir()

        # This entire thing is wrapped in a 
        # try/except/finally block to ensure
        # that whatever happens, we always
        # clean up the temporary directory.
        
        try:

            # ---------
            # Setup:

            # clone
            # - ghurl
            self.git_clone()

            # checkout
            # - head commit of pr
            self.git_checkout_pr()

            # submodules update
            self.submodules_update()

            # ---------
            # Test:

            # virtualenv setup
            self.virtualenv_setup()

            # snakemake
            self.snakemake()

            # build test status is a status update + link
            # for the outcome of the build test
            self.build_test_status()

            # serve test status is a staus update + link
            # for the built and served-up documentation
            self.serve_test_status()

            # virtualenv teardown
            self.virtualenv_teardown()

        except:

            # how to log traceback with logging?
            logging.error("Exception in the run() method!")

        finally:

            # ---------
            # Cleanup:

            # rm temporary directory
            rm_temp_dir()


    def validate(self,payload):
        """
        Validate the payload to ensure we should
        be running this task. If not, abort.
        """
        validated = False

        # must be a pull request
        if self.is_pull_request(payload):

            # must be a whitelisted repo
            if self.get_full_repo_name(payload) in self.repo_whitelist:

                # must be PR being opened or synced
                if self.is_pull_request_open(payload) \
                or self.is_pull_request_sync(payload):

                    validated = True

                else:
                    msg = "%s: validate(): Skipping task, "%(self.LABEL)
                    msg += "this payload's repository %s "%get_full_repo_name(payload)
                    msg += "is on the whitelist, but this PR is not "
                    msg += "being opened or synced."
                    logging.debug(msg)

            else:
                msg = "%s: validate(): Skipping task, "%(self.LABEL)
                msg += "this payload's repository %s "%get_full_repo_name(payload)
                msg += "is not on the whitelist: %s"%(", ".join(self.repo_whitelist))
                logging.debug(msg)

        else:
            msg = "%s: validate(): Skipping task, "%(self.LABEL)
            msg += "this payload for repository %s "%get_full_repo_name(payload)
            msg += "is not a pull request."
            logging.debug(msg)

        return validated







