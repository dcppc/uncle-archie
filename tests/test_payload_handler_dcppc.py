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
    def test_private_www_build_payload(self):
        """
        Test that sending a private-www (PR) build
        payload will trigger the correct task.
        """
        log_statements = [
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


