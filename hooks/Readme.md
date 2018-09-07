# Uncle Archie Continuous Integration Hooks

This directory contains scripts that are continous integration
hooks for Uncle Archie. Each file defines a `process_payload()`
that is imported by `../process_payload.py`.

Every time a webhook is received by Uncle Archie, it calls each
function with the webhook. Each hook script must use the payload
and meta-info provided to it to determine when it should run.

## TODO

These hook functions follow certain templates and borrow certain 
portions of code heavily from one another. These can be integrated
into objects that define methods to simplify the rote work and
make things re-usable and easier to set up.

