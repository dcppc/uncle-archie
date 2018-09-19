import archie

from .payload_handler_base import payload_handler_base
from .utils import \
        extract_payload, \
        post_pingpong_webhook, \
        post_pr_webhook, \
        post_new_branch_webhook, \
        post_pr_close_webhook, \
        post_pr_commit_to_master_webhook, \
        post_pr_sync_webhook

import logging
import os, sys
import json

"""
Test Merge Commit Payload Handler

This sets up Uncle Archie with the merge commit
test payload handler, and checks whether that
payload handler is correctly handled.

assertLogs:
https://docs.python.org/3/library/unittest.html#unittest.TestCase.assertLogs
"""

class test_merge_commit_payload_handler(payload_handler_base):
    """
    Test that merge commit webhooks are handled correctly
    """
    def test_pr(self):
        """
        Test that the webhook server correctly processes PR webhooks
        """
        log_statements = [
                'Is pull request open? False',
                'Is pull request sync? True',
                'Is pull request close? False',
                'Is this a merge commit? True',
                'Pull request number 81',
                'Pull request head commit: 48480b8022182a487e27c5f54ac1726da8e654e1',
                'Short repo name: private-www',
                'Full repo name: dcppc/private-www',
                'Repo clone url: https://github.com/dcppc/private-www.git',
                'Repo ssh url: git@github.com:dcppc/private-www.git',
                'Repo html url: https://github.com/dcppc/private-www',
        ]
        self.doit(
                'mc_test',
                post_pr_webhook,
                log_statements
        )

    def test_new_branch(self):
        """
        Test that the webhook server correctly processes new branch webhooks
        """
        log_statements = [
                "This is not a pull request payload",
        ]
        self.doit(
                'mc_test',
                post_new_branch_webhook,
                log_statements
        )

    def test_pr_close(self):
        """
        Test that the webhook server correctly processes close PR webhooks
        """
        log_statements = [
                "Is pull request open? False",
                "Is pull request sync? False",
                "Is pull request close? True",
                "Is this a merge commit? True",
                "Pull request number 38",
                "Pull request head commit: ba53185922e71c68404a0d74664806026622c9e1",
                "Short repo name: search-demo-mkdocs-material",
                "Full repo name: charlesreid1/search-demo-mkdocs-material",
                "Repo clone url: https://github.com/charlesreid1/search-demo-mkdocs-material.git",
                "Repo ssh url: git@github.com:charlesreid1/search-demo-mkdocs-material.git",
                "Repo html url: https://github.com/charlesreid1/search-demo-mkdocs-material",
        ]
        self.doit(
                'mc_test',
                post_pr_close_webhook,
                log_statements
        )

    def test_pr_commit_to_master(self):
        """
        Test that the webhook server correctly processes commit to master webhooks
        """
        log_statements = [
                "This is not a pull request payload",
        ]
        self.doit(
                'mc_test',
                post_pr_commit_to_master_webhook,
                log_statements
        )
    
    def test_pr_sync(self):
        """
        Test that the webhook server correctly processes PR sync webhooks
        """
        log_statements = [
                "Is pull request open? False",
                "Is pull request sync? True",
                "Is pull request close? False",
                "Is this a merge commit? True",
                "Pull request number 81",
                "Pull request head commit: 48480b8022182a487e27c5f54ac1726da8e654e1",
                "Short repo name: private-www",
                "Full repo name: dcppc/private-www",
                "Repo clone url: https://github.com/dcppc/private-www.git",
                "Repo ssh url: git@github.com:dcppc/private-www.git",
                "Repo html url: https://github.com/dcppc/private-www",
        ]
        self.doit(
                'mc_test',
                post_pr_sync_webhook,
                log_statements
        )

