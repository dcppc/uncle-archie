# uncle-archie

<img src="https://raw.githubusercontent.com/charlesreid1/uncle-archie/master/docs/images/unclearchiebk.svg?sanitize=true" width="100px"/>

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

Now create a custom function that takes two dictionaries
as input: one that contains the entire payload of the 
webhook, the other with meta-info about the webhook.
Put this in a Python file in the the `hooks/` directory. 
Simplest example:

```
def process_payload(payload,meta):
    pass
```

Last, edit `process_payload.py`, which calls all user-defined
hook functions when it receives a webhook, and include your
function in the list of functions called:

```
from hooks.just_print import process_payload as just_print

def process_payload(payload,meta):
    just_print(payload,meta)
```

This will include and call the user-defined function 
`process_payload()` in the file `hooks/just_print.py`.


