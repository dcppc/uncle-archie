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


