from .github_base import GithubTask

import logging


class GithubTestTask(GithubTask):
    """
    This task runs a test of every Github boolean test method
    """
    def run(self,payload,meta,config):
        msg = "%s: run(): Starting..."%(self.__class__.__name__)
        logging.debug(msg)

        pr_is_opened = self.is_pr_opened(payload)
        msg = "%s: run(): Is pull request open? %s"%(self.__class__.__name__,pr_is_opened)
        logging.debug(msg)

        pr_is_sync = self.is_pr_sync(payload)
        msg = "%s: run(): Is pull request sync? %s"%(self.__class__.__name__,pr_is_sync)
        logging.debug(msg)

        pr_is_close = self.is_pr_closed(payload)
        msg = "%s: run(): Is pull request closed? %s"%(self.__class__.__name__,pr_is_close)
        logging.debug(msg)

        is_merged = self.is_pr_closed_merged(payload)
        msg = "%s: run(): Is this PR closed via merging? %s"%(self.__class__.__name__,is_merged)
        logging.debug(msg)

        is_unmerged = self.is_pr_closed_unmerged(payload)
        msg = "%s: run(): Is this PR closed without merging? %s"%(self.__class__.__name__,is_unmerged)
        logging.debug(msg)

        pr_number = self.get_pull_request_number(payload)
        msg = "%s: run(): Pull request number %s"%(self.__class__.__name__,pr_number)
        logging.debug(msg)

        pr_head_commit = self.get_pull_request_head_commit(payload)
        msg = "%s: run(): Pull request head commit: %s"%(self.__class__.__name__,pr_head_commit)
        logging.debug(msg)

        short_repo_name = self.get_short_repo_name(payload)
        msg = "%s: run(): Short repo name: %s"%(self.__class__.__name__,short_repo_name)
        logging.debug(msg)

        full_repo_name = self.get_full_repo_name(payload)
        msg = "%s: run(): Full repo name: %s"%(self.__class__.__name__,full_repo_name)
        logging.debug(msg)

        clone_url = self.get_clone_url(payload)
        msg = "%s: run(): Repo clone url: %s"%(self.__class__.__name__,clone_url)
        logging.debug(msg)

        ssh_url = self.get_ssh_url(payload)
        msg = "%s: run(): Repo ssh url: %s"%(self.__class__.__name__,ssh_url)
        logging.debug(msg)

        html_url = self.get_html_url(payload)
        msg = "%s: run(): Repo html url: %s"%(self.__class__.__name__,html_url)
        logging.debug(msg)


class TestPRTask(GithubTestTask):
    """
    This task tests if this is a pull request payload
    """
    LABEL = "PR test task"
    def run(self,payload,meta,config):
        # This test checks PR webhooks only
        if self.is_pr(payload):
            super().run(payload,meta,config)
        else:
            msg = "TestPRTask: run(): This is not a pull request payload"
            logging.debug(msg)
            return


