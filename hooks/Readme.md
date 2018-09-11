# Uncle Archie Continuous Integration Hooks

This is the `hooks/` directory, which contains all the hooks
that are run by Uncle Archie to process webhooks.

Each time an incoming webhook is received, Uncle Archie creates
one and only one instance of each hook, and is agnostic to the
details of each test.

A singleton + factory method is implemented to return one
instance of each hook. This is called by the `process_payload.py`
script (one directory up), which is called by the flask webhook
server.


