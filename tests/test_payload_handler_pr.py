import archie

from .payload_handler_base import payload_handler_base

import logging
import os, sys
import json

"""
Test PR Payload Handler

This sets up Uncle Archie with the PR test 
payload handler, and checks whether that
payload handler is correctly handled.

Note that Uncle Archie can be run in non-test 
mode with this same PR handler by running the
script in:

    examples/example_payload_handler_pr.py

assertLogs:
https://docs.python.org/3/library/unittest.html#unittest.TestCase.assertLogs
"""

class test_pr_payload_handler(payload_handler_base):
    """
    Test that pull request webhooks are handled correctly
    """
    def test_pr_opened(self):
        """
        Test that the PR payload handler correctly processes PR webhooks
        """
        log_statements = [
                "Is pull request open? True",
                "Is pull request sync? False",
                "Is pull request close? False",
                "Is this PR closed via merging? False",
                "Is this PR closed without merging? False",
                "Pull request number 31",
                "Pull request head commit: be3465a25d140875770826d032928f39061c5973",
                "Short repo name: search-demo-mkdocs-material",
                "Full repo name: charlesreid1/search-demo-mkdocs-material",
                "Repo clone url: https://github.com/charlesreid1/search-demo-mkdocs-material.git",
                "Repo ssh url: git@github.com:charlesreid1/search-demo-mkdocs-material.git",
                "Repo html url: https://github.com/charlesreid1/search-demo-mkdocs-material",
        ]
        payload_handler = 'pr_build'
        self.doit(
                payload_handler,
                archie.tests.post_pr_opened,
                log_statements
        )

    def test_pr_closed_merged(self):
        """
        Test that the PR payload handler correctly processes merged closed PRs
        """
        log_statements = [
                "Is pull request open? False",
                "Is pull request sync? False",
                "Is pull request close? True",
                "Is this PR closed via merging? True",
                "Is this PR closed without merging? False",
                "Pull request number 9",
                "Pull request head commit: 0e9602c4140286350bededd267bd8f9d568f6a1b",
                "Short repo name: fake-docs",
                "Full repo name: charlesreid1/fake-docs",
                "Repo clone url: https://github.com/charlesreid1/fake-docs.git",
                "Repo ssh url: git@github.com:charlesreid1/fake-docs.git",
                "Repo html url: https://github.com/charlesreid1/fake-docs",
        ]
        self.doit(
                'pr_build',
                archie.tests.post_pr_closed_merged,
                log_statements
        )

    def test_pr_closed_unmerged(self):
        """
        Test that the PR payload handler correctly processes unmerged closed PRs
        """
        log_statements = [
                "Is pull request open? False",
                "Is pull request sync? False",
                "Is pull request close? True",
                "Is this PR closed via merging? False",
                "Is this PR closed without merging? True",
                "Pull request number 9",
                "Pull request head commit: 0e9602c4140286350bededd267bd8f9d568f6a1b",
                "Short repo name: fake-docs",
                "Full repo name: charlesreid1/fake-docs",
                "Repo clone url: https://github.com/charlesreid1/fake-docs.git",
                "Repo ssh url: git@github.com:charlesreid1/fake-docs.git",
                "Repo html url: https://github.com/charlesreid1/fake-docs",
        ]
        self.doit(
                'pr_build',
                archie.tests.post_pr_closed_unmerged,
                log_statements
        )

    def test_pr_sync(self):
        """
        Test that the PR payload handler correctly processes PR sync events 
        """
        log_statements = [
                "Is pull request open? False",
                "Is pull request sync? True",
                "Is pull request close? False",
                "Is this PR closed via merging? False",
                "Is this PR closed without merging? False",
                "Pull request number 81",
                "Pull request head commit: 48480b8022182a487e27c5f54ac1726da8e654e1",
                "Short repo name: private-www",
                "Full repo name: dcppc/private-www",
                "Repo clone url: https://github.com/dcppc/private-www.git",
                "Repo ssh url: git@github.com:dcppc/private-www.git",
                "Repo html url: https://github.com/dcppc/private-www",
        ]
        self.doit(
                'pr_build',
                archie.tests.post_pr_sync,
                log_statements
        )
    
