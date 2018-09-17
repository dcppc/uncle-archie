from .github_base import GithubTask

import logging

class TestPRTask(GithubTask):
    LABEL = "PR test task"
    def run(self,payload,meta,config):
        # This test checks PR webhooks only
        if not is_pull_request(payload):
            msg = "TestPRTask: run(): This is not a pull request payload"
            logging.debug(msg)
            return

        pr_is_open = is_pull_request_open(payload)
        msg = "TestPRTask: run(): Is pull request open? %s"%(pr_is_open)
        logging.debug(msg)

        pr_is_sync = is_pull_request_sync(payload)
        msg = "TestPRTask: run(): Is pull request sync? %s"%(pr_is_sync)
        logging.debug(msg)

        pr_is_close = is_pull_request_close(payload)
        msg = "TestPRTask: run(): Is pull request close? %s"%(pr_is_close)
        logging.debug(msg)

        is_merge = is_pull_request_merge_commit(payload)
        msg = "TestPRTask: run(): Is this a merge commit? %s"%(is_merge)
        logging.debug(msg)


        pr_number = get_pull_request_number(payload)
        msg = "TestPRTask: run(): Pull request number %s"%(pr_number)
        logging.debug(msg)

        pr_head_commit = get_pull_request_head_commit(payload)
        msg = "TestPRTask: run(): Pull request head commit: %s"%(pr_head_commit)
        logging.debug(msg)

        short_repo_name = get_short_repo_name(payload)
        msg = "TestPRTask: run(): Short repo name: %s"%(short_repo_name)
        logging.debug(msg)

        full_repo_name = get_full_repo_name(payload)
        msg = "TestPRTask: run(): Full repo name: %s"%(full_repo_name)
        logging.debug(msg)

        clone_url = get_clone_url(payload)
        msg = "TestPRTask: run(): Repo clone url: %s"%(clone_url)
        logging.debug(msg)

        ssh_url = get_ssh_url(payload)
        msg = "TestPRTask: run(): Repo ssh url: %s"%(ssh_url)
        logging.debug(msg)

        html_url = get_html_url(payload)
        msg = "TestPRTask: run(): Repo html url: %s"%(html_url)
        logging.debug(msg)


