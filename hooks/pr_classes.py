
class PRTestBase(PythonTask):
    """
    PR Test Base Class runs a test on PRs
    in whitelisted repos when the PR is opened
    or synced.

    This class defines the process_payload method
    to perform a git clone of whitelisted repos,
    check out the head commit of this PR, and
    call the test() method.

    This uses PythonTask as the base class
    so we can avoid multiple inheritance.
    """
    def process_payload(self,payload):
        # Here is where we decide on
        # our pattern for process_payload

        if not self.is_pull_request(payload):
            return

        if not (self.is_pull_request_open(payload)
                or self.is_pull_request_sync(payload)):
            return

        self.git_clone()

        self.git_checkout_pr_head()

        # test
        # test_success()
        # test_fail()

    def test(self):
        """
        Virtual method: actually run the PR test
        """
        err = "ERROR: PRTestBase: test(): "
        err += "This is a virtual method and must be overridden "
        err += "by a child class."
        logging.error(err)
        raise Exception(err)


    def test_fail(self):
        """
        Virtual method: run this when the PR test fails
        """
        err = "ERROR: PRTestBase: test_fail(): "
        err += "This is a virtual method and must be overridden "
        err += "by a child class."
        logging.error(err)
        raise Exception(err)


    def test_success(self):
        """
        Virtual method: run this when the PR test succeeds
        """
        err = "ERROR: PRTestBase: test_success(): "
        err += "This is a virtual method and must be overridden "
        err += "by a child class."
        logging.error(err)
        raise Exception(err)


    def git_clone(self):
        """
        Clone the git repository
        (We always use the temp dir, so no need
        to pass CWD or other into the method)
        """
        cmd = ['git','clone',gh_url]


    def git_checkout(self):
        pass

