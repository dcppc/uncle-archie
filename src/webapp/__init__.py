from ..payload_handlers import PayloadHandlerFactory
from flask import Flask, render_template
import os

CONFIG_FILE = 'config.json'

base = os.path.split(os.path.abspath(__file__))[0]

class UAFlask(Flask):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.payload_handler = None

    def set_payload_handler(self,handler_id):
        """
        Given a (string) payload handler ID,
        pass it to the factory to get a
        corresponding Payload Handler object
        of the correct type.
        """
        self.payload_handler = PayloadHandlerFactory(
                handler_id,
                self.config,
                **kwargs
        )

    def get_payload_handler(self,):
        """
        Get the payload handler that we have set
        """
        if self.payload_handler is None:
            err = "ERROR: UAFlask: get_payload_handler(): "
            err += "No payload handler has been set!"
            raise Exception(err)
        return self.payload_handler


app = UAFlask(
        __name__,
        #template_folder = os.path.join(base,'templates'),
        #static_folder = os.path.join(base,'static')
)

@app.route('/')
def index():

    # Load config
    config = util.get_config(CONFIG_FILE)

    # Verify webhooks are from github
    verify_github_source(config)

    # Play ping/pong with github
    event = request.headers.get('X-GitHub-Event', 'ping')
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

    payload_handler = app.get_payload_handler()
    payload_handler.process_payload(payload, meta, config)

    # Clean up
    return json.dumps({'status':'done'})


##############################################
# Flask utility functions

def load_config(json_file):
    """
    Load the Uncle Archie config file
    """
    try:
        pth = os.path.join(path, 'config.json')
        with open(pth, 'r') as cfg:
            return json.loads(cfg.read())
    except FileNotFoundError:
        logging.error("ERROR: No config file found at %s"%(pth))
        abort(501)

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

