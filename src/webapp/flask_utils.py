from .const import base, call

from flask import Flask, request, abort, render_template
import requests
import os, sys
import json
import logging

##############################################
# Flask utility functions

def verify_github_source(config):
    """
    Verify that the IP address of the server sending the
    payload is on the whitelist of github servers
    """
    if 'github_ips_only' in config and config['github_ips_only'] is True:
        whitelist = requests.get('https://api.github.com/meta').json()['hooks']
        for valid_ip in whitelist:
            if src_ip in ip_network(valid_ip):
                break
            else:
                logging.error('IP {} not allowed'.format(src_ip))
                abort(403)

def get_payload(request):
    """
    Gather the webhook payload data as JSON from the
    HTTP request received.
    """
    try:
        return request.get_json()
    except Exception:
        logging.warning('Request parsing failed')
        abort(400)


def enforce_secret(config,request):
    """
    Enforce secret (if user wants us to)
    """
    secret = config.get('enforce_secret', '')
    if secret:
        # Only SHA1 is supported
        header_signature = request.headers.get('X-Hub-Signature')
        if header_signature is None:
            abort(403)

        sha_name, signature = header_signature.split('=')
        if sha_name != 'sha1':
            abort(501)

        # HMAC requires the key to be bytes, but data is string
        mac = hmac.new(str.encode(secret), msg=request.data, digestmod='sha1')

        if not hmac.compare_digest(str(mac.hexdigest()), str(signature)):
            logging.error(' XXXXXXXX A webhook with an invalid secret was received.')
            abort(403)


def get_branch(payload):
    """
    Determine the branch this webhook is about
    """
    branch = ''
    event = request.headers.get('X-GitHub-Event')
    try:
        # Case 1: a ref_type indicates the type of ref.
        # This true for create and delete events.
        if 'ref_type' in payload:
            if payload['ref_type'] == 'branch':
                branch = payload['ref']
                return branch

        # Case 2: a pull_request object is involved. This is pull_request and
        # pull_request_review_comment events.
        elif 'pull_request' in payload:
            # This is the TARGET branch for the pull-request, not the source
            # branch
            branch = payload['pull_request']['base']['ref']
            return branch

        elif event in ['push']:
            # Push events provide a full Git ref in 'ref' and not a 'ref_type'.
            branch = payload['ref'].split('/', 2)[2]
            return branch

    except KeyError:
        # If the payload structure isn't what we expect, 
        # we'll live without the branch name
        return ""


