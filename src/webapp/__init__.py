from ..payload_handlers import PayloadHandlerFactory
from flask import Flask, request, abort, render_template
import os, sys
import json
import logging

CONFIG_FILE = 'config.json'

base = os.path.split(os.path.abspath(__file__))[0]

call = os.getcwd()

class UAFlask(Flask):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.payload_handler = None
        self.phf = PayloadHandlerFactory()
        logging.debug("="*40)
        logging.debug("="*40)
        logging.debug("flask __init__()")
        logging.debug("="*40)
        logging.debug("="*40)


    def set_payload_handler(self,handler_id,**kwargs):
        """
        Given a (string) payload handler ID,
        save it for later.
        
        Eventually we will pass it to the factory 
        to get a corresponding Payload Handler 
        object of the correct type.
        """
        self.payload_handler = None
        self.payload_handler_id = handler_id


    def get_payload_handler(self):
        if self.payload_handler is None:
            err = "ERROR: UAFlask: get_payload_handler(): "
            err += "No payload handler has been set!"
            logging.error(err)
            raise Exception(err)
        return self.payload_handler


    def del_payload_handler(self):
        """
        Delete the payload handler when we're done with the webhook
        """
        del self.payload_handler


    def init_payload_handler(self):
        """
        Use the PayloadHandler factory to initialize
        an instance of the payload handler that is 
        specified with self.payload_handler_id
        """
        if self.payload_handler_id is None:
            err = "ERROR: UAFlask: init_payload_handler(): "
            err += "No payload handler has been set!"
            logging.error(err)
            raise Exception(err)

        self.payload_handler = phf.factory(
                self.payload_handler_id,
                self.config,
        )

        return self.payload_handler


    def run(self,*args,**kwargs):
        """
        Extend the run method of the original
        Flask object to include two additional
        actions: load config, and instantiate
        the payload handler (and thus the task)
        object(s).
        """
        logging.debug("="*40)
        logging.debug("="*40)
        logging.debug("flask run() ")
        logging.debug("="*40)
        logging.debug("="*40)

        self.init_payload_handler()

        # ----------------------------
        # Load config
        msg = "UAFlask: run(): Preparing to load webapp config file.\n"
        loaded_config = False
        if 'UNCLE_ARCHIE_CONFIG' in os.environ:
            if os.path.isfile(os.path.join(call,os.environ['UNCLE_ARCHIE_CONFIG'])):
                # relative path
                self.config.from_pyfile(os.path.join(call,os.environ['UNCLE_ARCHIE_CONFIG']))
                loaded_config = True
                msg = "UAFlask: run(): Succesfuly loaded webapp config file from UNCLE_ARCHIE_CONFIG variable.\n"
                msg += "Loaded config file at %s"%(os.path.join(call,os.environ['UNCLE_ARCHIE_CONFIG']))
                logging.info(msg)
        
            elif os.path.isfile(os.environ['UNCLE_ARCHIE_CONFIG']):
                # absolute path
                self.config.from_pyfile(os.environ['UNCLE_ARCHIE_CONFIG'])
                loaded_config = True
                msg = "UAFlask: run(): Succesfuly loaded webapp config file from UNCLE_ARCHIE_CONFIG variable.\n"
                msg += "Loaded config file at %s"%(os.environ['UNCLE_ARCHIE_CONFIG'])
                logging.info(msg)
        
        else:
            err = "UAFlask: run(): Warning: No UNCLE_ARCHIE_CONFIG environment variable defined, "
            err += "looking for 'config.py' in current directory."
            logging.info(err)

            # hail mary: look for config.py in the current directory
            default_name = 'config.py'
            if os.path.isfile(os.path.join(call,default_name)):
                self.config.from_pyfile(os.path.join(call,default_name))
                loaded_config = True
                msg = "UAFlask: run(): Succesfuly loaded webapp config file with a hail mary.\n"
                msg += "Loaded config file at %s"%(os.path.join(call,'config.py'))
                logging.info(msg)

        if not loaded_config:
            err = "ERROR: UAFlask: run(): Problem setting config file with UNCLE_ARCHIE_CONFIG environment variable:\n"
            err += "UNCLE_ARCHIE_CONFIG value : %s\n"%(os.environ['UNCLE_ARCHIE_CONFIG'])
            err += "Missing config file : %s\n"%(os.environ['UNCLE_ARCHIE_CONFIG'])
            err += "Missing config file : %s\n"%(os.path.join(call, os.environ['UNCLE_ARCHIE_CONFIG']))
            logging.error(err)
            raise Exception(err)

        # ----------------------------
        # Run app
        super().run(*args,**kwargs)


app = UAFlask(
        __name__,
        template_folder = os.path.join(base,'templates'),
        static_folder = os.path.join(base,'static')
)


@app.route('/', methods=['GET', 'POST'])
def index():

    # forgot to add the dang render template handler
    if request.method=='GET':
        return render_template("index.html")

    config = app.config

    # Verify webhooks are from github
    verify_github_source(config)

    # Play ping/pong with github
    event = request.headers.get('X-GitHub-Event')
    if event == 'ping':
        return json.dumps({'msg': 'pong'})

    # Get the payload
    payload = get_payload(request)

    # Enforce secret
    enforce_secret(config,request)

    # Get the branch
    branch = get_branch(payload)

    # Current events almost always have a repository.
    # Be safe in case they do not.
    name = payload['repository']['name'] if 'repository' in payload else None

    # Assemble quick lookup info
    meta = {
        'name': name,
        'branch': branch,
        'event': event
    }

    payload_handler = get_payload_handler()
    payload_handler.process_payload(payload, meta, config)

    del_payload_handler()

    # Clean up
    return json.dumps({'status':'done'})


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

