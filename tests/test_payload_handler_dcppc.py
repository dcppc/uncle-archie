import archie

from .payload_handler_base import payload_handler_base

import logging
import os, sys
import json

"""
Test DCPPC Payload Handler

This sets up Uncle Archie with all the DCPPC
payload handlers, and checks each individual
Task by sending a test payload that will 
trigger each Task.
"""

class test_pr_payload_handler(payload_handler_base):
    def test_private_www_build_sync_payload(self):
        """Test private-www PR sync payload with private-www build task."""
        log_statements = [
                'UncleArchieTask: __init__(): Starting constructor',
                'Task name: private_www_PR_builder',
                'UncleArchieTask: __init__(): Success!',
                'PyGithubTask: __init__(): New virtual environment will be named "vp"',
                'UncleArchieTask: run_cmd(): Finished running "git clone" command',
                'UncleArchieTask: run_cmd(): Finished running "git checkout" command',
                'UncleArchieTask: run_cmd(): Finished running "submodule update" command',
                'PyGithubTask: virtualenv_setup(): Success!',
                'UncleArchieTask: run_cmd(): Finished running "pip install" command',
                'UncleArchieTask: run_cmd(): Finished running "snakemake build" command',
                'PyGithubTask: virtualenv_setup(): Success!',
                'private-www build test succes:',
        ]
        payload_handler = 'dcppc'
        self.doit(
                payload_handler,
                archie.tests.dcppc_private_www_sync,
                log_statements
        )


    def test_private_www_build_closed_merged_payload(self):
        """Test private-www PR closed (merged) payload with private-www build task."""
        log_statements = [
                'UncleArchieTask: __init__(): Starting constructor',
                'Task name: private_www_PR_builder',
                'UncleArchieTask: __init__(): Success!',
                'PyGithubTask: __init__(): New virtual environment will be named "vp"',
                'private_www_PR_builder: run(): Beginning to run task',
                'private_www_PR_builder: validate(): Skipping task'
        ]
        payload_handler = 'dcppc'
        self.doit(
                payload_handler,
                archie.tests.dcppc_private_www_closed_merged,
                log_statements
        )


    def test_private_www_build_closed_unmerged_payload(self):
        """Test private-www PR closed (unmerged) payload with private-www build task."""
        log_statements = [
                'UncleArchieTask: __init__(): Starting constructor',
                'Task name: private_www_PR_builder',
                'UncleArchieTask: __init__(): Success!',
                'PyGithubTask: __init__(): New virtual environment will be named "vp"',
                'private_www_PR_builder: run(): Beginning to run task',
                'private_www_PR_builder: validate(): Skipping task'
        ]
        payload_handler = 'dcppc'
        self.doit(
                payload_handler,
                archie.tests.dcppc_private_www_closed_unmerged,
                log_statements
        )


    def test_private_www_build_push_payload(self):
        """Test private-www push payload with private-www build task."""
        log_statements = [
                'UncleArchieTask: __init__(): Starting constructor',
                'Task name: private_www_PR_builder',
                'UncleArchieTask: __init__(): Success!',
                'PyGithubTask: __init__(): New virtual environment will be named "vp"',
                'private_www_PR_builder: run(): Beginning to run task',
                'private_www_PR_builder: validate(): Skipping task'
        ]
        payload_handler = 'dcppc'
        self.doit(
                payload_handler,
                archie.tests.dcppc_private_www_push,
                log_statements
        )


