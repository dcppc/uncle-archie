from .github_base import GithubTask

import logging


class GithubTestTask(GithubTask):
    def run(self,payload,meta,config):
        pr_is_open = self.is_pull_request_open(payload)
        msg = "%s: run(): Is pull request open? %s"%(self.__class__.__name__,pr_is_open)
        logging.debug(msg)

        pr_is_sync = self.is_pull_request_sync(payload)
        msg = "%s: run(): Is pull request sync? %s"%(self.__class__.__name__,pr_is_sync)
        logging.debug(msg)

        pr_is_close = self.is_pull_request_close(payload)
        msg = "%s: run(): Is pull request close? %s"%(self.__class__.__name__,pr_is_close)
        logging.debug(msg)

        is_merge = self.is_pull_request_merge_commit(payload)
        msg = "%s: run(): Is this a merge commit? %s"%(self.__class__.__name__,is_merge)
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
    LABEL = "PR test task"
    def run(self,payload,meta,config):
        # This test checks PR webhooks only
        if not self.is_pull_request(payload):
            msg = "TestPRTask: run(): This is not a pull request payload"
            logging.debug(msg)
            return
        else:
            super().run(payload,meta,config)

class TestMergeCommitTask(GithubTestTask):
    LABEL = "merge commit test task"
    def run(self,payload,meta,config):
        # This test checks PR webhooks only
        if not self.is_pull_request_merge_commit(payload):
            msg = "TestMergeCommitTask: run(): This is not a pull request merge commit payload"
            logging.debug(msg)
            return
        else:
            super().run(payload,meta,config)

class TestNewBranchTask(GithubTestTask):
    LABEL = "new branch test task"
    def run(self,payload,meta,config):
        # This test checks PR webhooks only
        if not self.is_pull_request_merge_commit(payload):
            msg = "TestNewBranchTask: run(): This is not a new branch commit payload"
            logging.debug(msg)
            return
        else:
            super().run(payload,meta,config)

