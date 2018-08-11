# How Payloads Are Processed

Uncle Archie runs a Flask server to receive webhooks.
Github sends webhooks in the form of JSON to the Flask
server when events occur on Github. The JSON file contains
lots of information about the event.

The JSON webhook is converted to a Python dictionary and is
passed to the `process_payload()` function defined in 
`process_payload.py`. 

## Hooks

Directory: [`hooks/`](https://github.com/charlesreid1/uncle-archie/tree/master/hooks)

Each incoming webhook payload is passed to a set of hook functions,
which are Python functions that live in the `hooks/` folder.
These are imported and called by `process_python.py`.

See [Hooks](hooks.md) for details about how the hooks work
and how to define new ones.

## Payload Museum

To see examples of payloads, visit the 
Payload Museum in the `museum/` directory
of the repository.

## Uncle Archie Configuration File

File: [`config.json`](https://github.com/charlesreid1/uncle-archie/blob/master/config.example.json)

The configuration file `config.json` contains **both** Flask **and** 
back end hook function configuration details.

An example of a Flask configuration variable is the secret key that
must be included with the webhook's header for the webhook to be
processed.

An example of a back end hook function's configuration detail is
the Github API access token for the bot account that Uncle Archie
uses, which is only used in the hook functions to interact with
the Github API.

(API keys are sensitive information so this file 
should be kept secret, hence the configuration file
is in `.gitignore`).

The config is loaded by the Flask application, since it contains
flask-specific configuration details. The configuration is then
handed off to the process payload function, which passes it on 
to each hook function.

It is available via the variable `conf`.

