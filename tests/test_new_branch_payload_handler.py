import archie

from .payload_handler_base import payload_handler_base
from .utils import \
        extract_payload, \
        post_pingpong_webhook, \
        post_pr_webhook, \
        post_new_branch_webhook, \
        post_close_pr_webhook, \
        post_pr_commit_to_master_webhook, \
        post_pr_sync_webhook

import logging
import os, sys
import json

"""
Test New Branch Payload Handler

This sets up Uncle Archie with the new branch
test payload handler, and checks whether that
payload handler is correctly handled.

assertLogs:
https://docs.python.org/3/library/unittest.html#unittest.TestCase.assertLogs
"""

class test_new_branch_payload_handler(payload_handler_base):
    pass








