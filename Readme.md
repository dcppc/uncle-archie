# uncle-archie

<img src="https://raw.githubusercontent.com/charlesreid1/uncle-archie/master/docs/images/unclearchiebk.svg?sanitize=true" width="100px"/>

> _"But, I say," said Archie, "it's all a mistake, you know. Absolutely_
> _a frightful error, my dear old constables. I'm not the lad you're_
> _after at all. The chappie you want is a different sort of fellow_
> _altogether. Another blighter entirely."_
> 
> _\- P. G. Wodehouse,_ The Indiscretions of Archie

**Uncle Archie** is a home-brewed continuous integration server.
It handles pull request checks (build-test) and push-to-deploy 
functionality (build-test-deploy). It is written in Python
and uses PyGithub.

**Uncle Archie** is intended to run behind an nginx reverse proxy
so that SSL can be used. This requires that the server running 
Uncle Archie be accessible via a domain name, and not just a bare 
IP address.

Documentation: <https://pages.charlesreid1.com/uncle-archie> or [`docs/index.md`](docs/index.md)

Source code: <https://git.charlesreid1.com/bots/uncle-archie>

Source code mirror: <https://github.com/charlesreid1/uncle-archie>

## Quick Start

To get started, run the Uncle Archie Flask server:

```
python uncle_archie.py
```

This will use the available/built-in Python functions as
payload-processing hooks.

To create your own custom function that processes payload hooks,
define a custom function that takes the payload, a dictionary
of meta-info (repo, branch name, and action name), and the 
configuration dictionary:

```
def process_payload(payload, meta, config):
    # Do some stuff here, 
    # like use the payload to see
    # if this is an event we are 
    # interested in, or create a 
    # Github API instance.
    pass
```

Put this in a Python file in the the `hooks/` directory:

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

