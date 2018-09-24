from .github_base import PyGithubTask

from urllib.parse import urljoin
import yaml

class private_www_PR_builder(PyGithubTask):
    """
    Builds pull requests on the private-www repo.
    """
    LABEL = "private_www_PR_builder"

    def run(self,payload,meta,config):
        """
        This is the main method that runs the task.
        """
        super().run(payload,meta,config)

        msg = "%s: run(): Beginning to run task"%(self.LABEL)
        logging.debug(msg)

        # Abort if not right kind of webhook
        # (this method logs for us)
        if not self.validate(payload):
            return

        # We don't need to share info or pass lots of params.
        # Rather, each method is passed the payload and uses
        # this class's utility methods to get the info it needs.

        # Internal flag used to stop on errors
        self.abort = False


        # ---------------------
        # The following is in a giant 
        # try/except/finally block to ensure
        # that whatever happens, we always
        # clean up the temporary directory.

        # Create a temporary working directory
        self.make_temp_dir()

        msg = "%s: run(): Made temporary directory at %s"%(self.temp_dir)
        logging.debug(msg)

        # Each command below takes care of its own logging
        
        try:

            # ---------
            # Setup:

            # clone
            # - ghurl
            self.git_clone(payload)

            # checkout
            # - head commit of pr
            self.git_checkout_pr(payload)

            # submodules update
            self.submodules_update(payload)

            # adjust base_url in mkdocs.yml
            self.modify_mkdocs_yml()

            # ---------
            # Test:

            # virtualenv setup
            self.virtualenv_setup()

            # snakemake
            outcome = self.snakemake(payload)

            # virtualenv teardown
            self.virtualenv_teardown()

            # build test: outcome of the snakemake build test
            # move results to htdocs dir
            self.build_test_url_prep(payload)
            # set commit status
            self.build_test_status_update(payload)

            # serve test: built and served-up documentation
            # move results to htdocs dir
            self.serve_test_url_prep(payload)
            # set commit status
            self.serve_test_status_update(payload)

        except:
            logging.exception("Exception in the run() method!")

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


    #############################################
    # Setup methods

    # Question: what happens when we have
    # complicated directories and cwd?
    # We're not passing things around
    # right now, but... what happens when
    # we do?
    # 
    # A:
    # (Construct them when we need them.
    # If a construction is too complicated,
    #  make a utility method.)
    # (Everybody can access temp_dir
    #  anyway, right??)


    def git_clone(self,payload):
        # get ghurl
        ghurl = self.get_ssh_url(payload)

        # run git clone command
        clonecmd = ['git','clone','--recursive',ghurl]
        self.abort = run_cmd(
                clonecmd,
                "git clone",
                self.temp_dir
        )


    def git_checkout_pr(self,payload):
        if not self.abort:
            # get head pr from payload
            head_commit = get_pull_request_head_commit(payload)

            # get repo dir
            repo_short_name = self.get_short_repo_name(payload)
            repo_dir = os.path.join(self.temp_dir,repo_short_name)

            # checkout head pr
            cocmd = ['git','checkout',head_commit]
            self.abort = run_cmd(
                    cocmd,
                    "git checkout",
                    repo_dir
            )


    def submodules_update(self,payload):
        # run submodules update init
        if not self.abort:
            # get repo dir
            repo_short_name = self.get_short_repo_name(payload)
            repo_dir = os.path.join(self.temp_dir,repo_short_name)

            # checkout head pr
            sucmd = ['git','submodule','update','--init']
            self.abort = run_cmd(
                    sucmd,
                    "submodule update",
                    repo_dir
            )


    #############################################
    # Setup methods


    def modify_mkdocs_yml(self,payload):
        """
        We must modify mkdocs.yml and update the
        base_url parameter for this to work with our
        fake hosted docs site.
        """
        if self.debug:
            return True

        mkdocs_yml_file = os.path.join(self.temp_dir,repo_short_name,'mkdocs.yml')
        with open(mkdocs_yml_file,'r') as f:
            lines = f.readlines()

        for i,line in enumerate(lines):
            if 'base_url' in line:
                # this should give us a dictionary
                # with key base_url and value (url)
                contents = yaml.load(line)
                contents = contents[0]
                contents['base_url'] = self.base_url
                lines[i] = yaml.dump(contents, default_flow_style=False)

        with open(mkdocs_yml_file,'w') as f:
            f.write("\n".join(lines))


    def snakemake(self,payload):
        """
        Run the snakemake build command
        (this is the money shot).

        Return true if command succeeds,
        otherwise return false.
        """
        if not self.abort:
            # get repo dir
            repo_short_name = self.get_short_repo_name(payload)
            repo_dir = os.path.join(self.temp_dir,repo_short_name)

            buildcmd = ['snakemake','--nocolor','build_docs']
            self.abort = run_cmd(
                    buildcmd,
                    "snakemake build",
                    repo_dir
            )

            if not self.abort:
                # passed the test
                return True

        return False


    def build_test_url_prep(self,payload): 
        """
        Move files to prepare the output log
        to be hosted in the htdocs dir
        """
        # copy self.temp_dir,self.log_file
        # to self.htdocs_dir,self.log_file
        pass


    def build_test_status_update(self,payload): 
        # get head pr from payload
        full_repo_name = None
        head_commit = get_pull_request_head_commit(payload)
        pass_msg = 'Uncle Archie Task: %s: Success!'%(self.LABEL)
        fail_msg = 'Uncle Archie Task: %s: Task failed.'%(self.LABEL)
        status_url = urljoin(self.base_url,self.log_file)

        if self.abort is False:
            try:
                # state success
                self.set_commit_status(
                        full_repo_name,
                        head_commit,
                        "success",
                        pass_msg,
                        self.label,
                        status_url
                )
            except GithubException as e:
                logging.error("Github error: commit status failed to update.")

            logging.info("private-www build test succes:")
            logging.info("    Commit %s"%head_commit)
            logging.info("    PR %s"%pull_number)
            logging.info("    Repo %s"%full_repo_name)
            logging.info("    Link %s"%status_url)

        else:
            try:
                self.set_commit_status(
                        full_repo_name,
                        head_commit,
                        "failure",
                        fail_msg,
                        self.label,
                        status_url
                )
            except GithubException as e:
                logging.error("Github error: commit status failed to update.")

            logging.info("private-www build test failure:")
            logging.info("    Commit %s"%head_commit)
            logging.info("    PR %s"%pull_number)
            logging.info("    Repo %s"%full_repo_name)
            logging.info("    Link %s"%status_url)



    def serve_test_url_prep(self,payload): 
        """
        Move documentation output from snakemake build 
        to be hosted in the htdocs dir
        """
        # copy self.temp_dir,repo_dir,site
        # to self.htdocs_dir,unique_dir,X
        pass




    def serve_test_status_update(self,payload): 
        pass

