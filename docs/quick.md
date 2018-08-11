## Quick Start

To get started, clone a local copy of the Uncle Archie repo:

```
git clone git@github.com:charlesreid1/uncle-archie
cd uncle-archie
```

Next, run the Uncle Archie Flask server in a virtual environment:

```
virtualenv vp
source vp/bin/activate
vp/bin/pip install -r requirements.txt
vp/bin/python uncle_archie.py
```

This will start the Uncle Archie Flask server at 
`http://localhost:5005`.

We use Uncle Archie behind an Nginx reverse proxy (see the
[Nginx](nginx.md) page), which enables accessing Uncle Archie
via an HTTPS address at a trusted domain name like
`https://archie.mydomain.com`.


### Defining Your First Hook Function:

Uncle Archie receives incoming webhooks from Github, and
passes each webhook to a set of Python hook functions.
There are several hook functions included with Uncle
Archie, see the `hooks/` directory.

To write your first hook function, create a new file in
`hooks/` that defines a function 
`process_payload(payload, meta, config)`,
where all arguments are dictionaries.

```
def process_payload(payload, meta, config):

    # Do some stuff here

    pass
```

Put this in a Python file in the `hooks/` directory:

```
cat > hooks/my_cool_hook.py <<EOF
def process_payload(payload, meta, config):
    # Do some stuff here, 
    # like use the payload to see
    # if this is an event we are 
    # interested in, or create a 
    # Github API instance.
    pass
EOF
```

Now edit `process_payload.py` in the repo so that it loads
this new hook:

```
# ...
# other import statements
# ...
from hooks.my_cool_hook import process_payload as my_cool_hook

def process_payload(payload,meta,config):
    # ...
    # other function calls
    # ...
    my_cool_hook(payload,meta,config)
```

Uncle Archie will now call the new hook every time an incoming webhook
is received by the Flask server.


### Sending Github Webhooks to Uncle Archie:

Github will only send webhooks to Uncle Archie if webhooks are set up
in a Github repository.

To have Uncle Archie run CI tests in a given repo, like 
`coolkid/mycoolrepo`, visit the repository in Github
and go to the repository Settings. Select Webhooks from
the menu. Select Add Webhook.

For the URL endpoint, enter the address at which Github
can reach your webhook server. This is where having a 
proper [Nginx](nginx.md) setup with SSL becomes important.

For the secret, enter the same secret that is in the 
Flask configuration file `config_flask.py`. 

For the type of events to deliver, you should select
the types of events you want your hook function to react to.
In the next section we'll make a hook function that reacts
to pull request events, so try selecting the two "Pull Request"
options. Save the webhook.

Github will test your webhook server by sending a "ping"
message; it expects "pong" back. If your server is reachable
and responds with pong, the webhook will have a green check,
otherwise a red x.


### A More Interesting Pull Request Hook Function

The hook function above is really boring, so let's replace it with
a slightly more interesting one. This one inspects the payload
to look for pull request events that open new pull requests 
or modify existing pull requests:

```
cat > hooks/my_cool_hook.py <<EOF
def process_payload(payload, meta, config):
    
    if 'pull_request' not in payload.keys():
        # This is not a pull request
        return

    if 'action' not in payload.keys():
        # This is not a pull request action
        return

    if payload['action'] not in ['opened','synchronize']:
        # This pull request event is not interesting -
        # neither opening a new PR,
        # nor modifying an existing PR
        return

    # Get the repository name
    full_repo_name = payload['repository']['full_name']

    # Implement some sort of whitelist
    # of repositories that you expect
    # incoming webhooks from.

    # Get the head commit
    head_commit = payload['pull_request']['head']['sha']

    # This message isn't going to go anywhere useful,
    # so write files on disk if you need to store/export data
    print("The current commiti is %s"%(head_commit))
    pass
EOF
```

You can find other hook functions in the `hooks/` directory of the 
repository.

