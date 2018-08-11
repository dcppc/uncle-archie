# Hooks

## What Are Hooks

Each incoming webhook payload is passed to a set of hook functions,
which are Python functions that live in the `hooks/` folder.
These are imported and called by `process_python.py`.

## How Are Hook Functions Defined?

A hook is a Python file living in the `hooks/` directory.
it should define one method `process_payload()` with the 
same signature as the `process_payload()` method in 
`process_payload.py`.

The new hook function should also be imported in the file
`process_payload.py` - this contains a series of calls to
hook functions, and this occurs for each webhook received.

## How To Define A New Hook Function?

To make a new hook function:

* Add a python file to `hooks/`
* Define a method `process_payload()` (following `process_payload.py`)
* Import hook in `process_payload.py`

And you're done defining your hook.

## How To Use A New Hook Function?

Once you have defined a new hook function, and 
it is being called from `process_payload.py`,
you must restart the Uncle Archie Flask server.

To instruct Github to send webhooks for 
events in your repository to Uncle Archie,
you must activate webhooks in the repositories
where you want Uncle Archie to run.

See [Activating Hooks in Github](github.md).

